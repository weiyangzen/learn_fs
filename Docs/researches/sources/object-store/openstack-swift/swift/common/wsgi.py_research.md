# sources/object-store/openstack-swift/swift/common/wsgi.py

## Purpose
This module provides Swift's WSGI configuration loading, pipeline construction, socket binding, eventlet server execution, process-management strategies, request-processor initialization, and helper functions for creating internal subrequests. It is the common startup and in-process WSGI toolkit for Swift proxy and storage services.

## Important APIs, Types, and Functions
- `NamedConfigLoader`, `ConfigDirLoader`, `_loadconfigdir()`, and `ConfigString` extend PasteDeploy to preserve section names, load config directories, and support raw config strings.
- `wrap_conf_type()`, `appconfig`, `loadcontext()`, `loadapp()`, and `load_app_config()` normalize config paths and build PasteDeploy apps/pipelines, allowing the final app to modify the pipeline.
- `get_socket(conf)` validates `bind_port`/`keep_idle`, binds TCP sockets with backlog and retry timeout, optionally wraps testing SSL, and configures keepalive and TCP_NODELAY.
- `RestrictedGreenPool` blocks accept-loop progress when `max_clients == 1`, making single-client mode truly serial.
- `PipelineWrapper` inspects and edits PasteDeploy pipeline contexts before instantiation.
- `run_server()` loads the app, selects Swift HTTP protocol or PROXY protocol, creates the eventlet WSGI server, calls readiness callbacks, and cleans up pools/watchdogs.
- `StrategyBase`, `WorkersStrategy`, and `ServersPerPortStrategy` implement prefork worker lifecycle, seamless reload state transfer, per-port object-server binding, child tracking, stale reload worker cleanup, and listen-socket management.
- `check_config()` and `run_wsgi()` validate config, configure logging, monkey patch, choose a strategy, daemon hygiene, fork workers, handle signals, and perform reload/stop choreography.
- `_initrp()` and `init_request_processor()` load an app plus config/logger for command-line tools or embedded use.
- `WSGIContext`, `make_env()`, `make_subrequest()`, `make_pre_authed_env()`, and `make_pre_authed_request()` support middleware-internal calls and response inspection.

## Control Flow and Behavior
Startup flows through `run_wsgi()`: `check_config()` loads app config via PasteDeploy, sets `swift_dir`, validates configuration, builds a logger, optionally disables fallocate, monkey patches eventlet, loads the app once for validation, and creates either `WorkersStrategy` or `ServersPerPortStrategy`. `run_wsgi()` then cleans daemon hygiene, either runs a no-fork server or enters a parent loop that forks child workers, waits for each child to write `ready`, signals readiness, waits for exits, and responds to SIGTERM/SIGHUP/SIGUSR1.

`WorkersStrategy` owns one listen socket and maintains a fixed worker count. `ServersPerPortStrategy` uses `BindPortsCache` to discover local ring ports and starts a configured number of workers per port, rebinding as ports appear. `StrategyBase.signal_ready()` captures stdio, informs old managers via inherited fd, reads stale worker state, and notifies systemd. SIGUSR1 reload marks sockets close-on-exec, forks a temporary child that closes old sockets after the new process signals readiness, serializes old worker PIDs through `CHILD_STATE_FD_ENV_KEY`, then `execv()`s the current script.

Pipeline loading builds the ultimate app first, allows `modify_wsgi_pipeline()`, then instantiates filters in reverse. It tracks a separate `ProxyLoggingMiddleware` around the final app so backend internal requests can log correctly.

## State and Persistence
The module mutates process state extensively: signal handlers, environment variables for reload fds, timezone `TZ=UTC+0`, eventlet hub/debug settings, systemd notifications, forked child processes, listen sockets, stdio capture, and global PasteDeploy loader registration. Persistent disk state is not created directly, but config files/directories and ring port caches drive runtime behavior.

## Dependencies and Integration Points
It depends on eventlet and Swift's concurrency facade, PasteDeploy, Swift HTTP protocol classes, constraints, swob `Request`, logging utilities, `BindPortsCache`, daemon hygiene helpers, systemd notification helpers, and storage-policy/ring configuration. It is called by Swift service entrypoints and used by middleware to synthesize subrequests.

## Risks and Edge Cases
- Process management is signal- and fork-heavy; reload fd handling and close-on-exec flags are critical to avoid duplicate listeners or stalled old workers.
- `get_socket()` only warns for inline SSL and assumes external TLS in production.
- Config compatibility depends on PasteDeploy internals that are monkey patched at import time.
- `ServersPerPortStrategy` must handle dynamic ring port changes without leaking sockets or workers.
- `make_env()` copies a curated set of WSGI keys; missing future environment keys can affect middleware subrequests.
- Child readiness depends on exact `b'ready'` pipe writes; worker startup failures raise in the manager.

## Test Signals
Tests should exercise config file, config dir, and config string loading; pipeline modification and request-logging split pipeline attributes; socket bind validation and retries; no-fork versus prefork paths; SIGTERM/SIGHUP/SIGUSR1 behavior; per-port worker registration and stale worker cleanup; systemd notification hooks; generated pre-authorized requests; and `WSGIContext` response capture when apps delay `start_response`.
