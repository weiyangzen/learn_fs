# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_conn.c

## Purpose

Implements the connection-level checkpoint server. It parses checkpoint scheduling configuration, starts/stops the background checkpoint thread, runs periodic or log-size-triggered checkpoints, and exposes a signal path for log writers to wake the server.

## Important APIs, Types, And Functions

`__wt_checkpoint_server_create` configures and starts the server, destroying any existing server first during reconfigure. `__wt_checkpoint_server_destroy` stops the thread, joins it, destroys its condition variable, closes its internal session, and clears server fields. `__wt_checkpoint_signal` wakes the server when enough log bytes have been written. Internal helpers are `__ckpt_server_config`, `__ckpt_server_run_chk`, `__ckpt_server`, and `__ckpt_server_start`.

State lives in `WT_CONNECTION_IMPL::ckpt.server` (`WTI_CKPT_THREAD`), `conn->server_flags`, log manager flags and file size, and the checkpoint generation counter.

## Control Flow

Configuration reads `checkpoint.wait` into microseconds and `checkpoint.log_size` into an atomic logsize field. If either wait is nonzero or log-size checkpointing is enabled with logging, it validates that the connection is not in-memory, raises log-size to at least the log file maximum when needed, resets log-written counters, and requests server start. Start sets `WT_CONN_SERVER_CHECKPOINT`, opens an internal checkpoint-server session with wait capability, allocates a condition variable, creates the thread, and marks `tid_set`.

The server thread waits on the condition variable for the configured interval or explicit signal. After wakeup it exits if the server flag was cleared, otherwise records the current checkpoint generation and calls `WT_SESSION::checkpoint`. If a real checkpoint advanced the generation and log-size scheduling is active, it resets log-written counters, clears the signalled flag, and performs a one-microsecond wait to drain a stale signal so it does not immediately checkpoint again.

Destroy clears the server flag, signals and joins the thread if running, destroys synchronization state, closes the internal session, and zeroes scheduling fields. `__wt_checkpoint_signal` compares the supplied log byte count against the configured threshold and signals only once until the server resets `signalled`.

## State And Persistence Behavior

The server itself is transient, but it triggers durable checkpoints through the normal session checkpoint API. Its persistent effect is indirect: periodic or log-size-triggered metadata, btree, block-manager, and log checkpoint state written by the checkpoint transaction machinery. Runtime scheduling state includes interval, log-size threshold, signal coalescing, thread/session/condition handles, and the server flag.

## Dependencies And Integration Points

Depends on config parsing, the log subsystem (`WT_LOG_ENABLED`, `conn->log_mgr.file_max`, `__wt_log_written_reset`), internal sessions, condition variables, thread APIs, connection server flags, checkpoint generation, public session checkpoint API, and panic handling. It is invoked during connection open and reconfigure and is signaled by log-writing paths.

## Risks

Reconfigure intentionally bounces the server to avoid racing live config reads; failure to destroy cleanly would leave stale sessions or condvars. Log-size checkpointing is valid only when logging is enabled and uses a minimum of log file size to avoid too-frequent checkpoints. In-memory configuration is incompatible and must fail early. Signal coalescing through `signalled` is not atomic; it relies on server/log scheduling assumptions and can skip redundant signals, so tests should watch for missed log-size checkpoints.

## Test Signals

Coverage should include wait-based checkpoints, log-size-triggered checkpoints with logging, no server when both wait/log-size are zero, in-memory incompatibility errors, reconfigure stop/start, clean shutdown with no leaked internal session, and log-written reset only after a non-skipped checkpoint advances `WT_GEN_CHECKPOINT`.
