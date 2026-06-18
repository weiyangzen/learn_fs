# sources/storage-engines/tikv/components/server/src/signal_handler.rs

Purpose: platform-specific signal loop for TiKV process control and diagnostic dumping. On Unix it converts OS signals into service events or metric/stat dumps; non-Unix builds provide a no-op shim.

Important APIs and functions: public re-export `wait_for_signal`. Unix `wait_for_signal` accepts optional engines, optional Rocks statistics, config controller, and optional service event sender. It listens for `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGUSR1`, and `SIGUSR2`.

Control flow: `SIGTERM` checks current `server.graceful_shutdown_timeout`; if non-zero it sends `ServiceEvent::GracefulShutdown`, otherwise `ServiceEvent::Exit`, then breaks. `SIGINT` and `SIGHUP` send `Exit` and break. `SIGUSR1` logs TiKV metrics plus optional KV and raft engine stats and Rocks statistics. `SIGUSR2` is registered but falls through to the unreachable arm because only `SIGUSR1` is handled as a diagnostic signal.

State and persistence behavior: no persistent writes. It reads current config dynamically, sends messages through TiKV mpsc, and logs diagnostics.

Dependencies and integration points: used by `server2.rs` in a background thread after server startup. Integrates `signal_hook`, TiKV metrics, `service::ServiceEvent`, `ConfigController`, and engine statistic dumping.

Risks: if the service event channel is disconnected, shutdown signals only log a warning and the signal loop exits. Graceful shutdown behavior can change at runtime because it reads the current config at signal time. Non-Unix function signature differs from Unix by omitting `ConfigController`, which is hidden behind cfg but worth preserving carefully.

Test signals: no direct unit tests. Behavior is mostly covered by integration/manual signal tests.
