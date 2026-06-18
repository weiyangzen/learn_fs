# sources/object-store/garage/src/garage/server.rs

Purpose: This file launches and coordinates a Garage daemon. It reads config with resolved secrets, initializes the core `Garage` object, optionally applies single-node/default-key/default-bucket bootstrap, starts background workers, tracing, internal RPC, public S3/K2V/Web/Admin servers, and then handles graceful shutdown.

Important APIs and types: `run_server` is the main async entrypoint. `initial_config` implements `--single-node`, `--default-access-key`, and `--default-bucket`. `watch_shutdown_signal` has Unix and Windows implementations. The file uses `Garage`, `BackgroundRunner`, `AdminApiServer`, `S3ApiServer`, optional `K2VApiServer`, `WebServer`, and `tokio::sync::watch`.

Control flow: `run_server` reads config, initializes metrics exporter when enabled, creates `Garage`, runs bootstrap config, creates shutdown watch channel and background runner, spawns workers, initializes OTLP tracing if configured, constructs API servers, starts the RPC system, pushes enabled public servers into a join list, and waits until either shutdown-only or all server tasks finish. Shutdown deregisters RPC handlers, shuts down OpenTelemetry, awaits NetApp, cleans up system references, drops `Garage`, and waits for background tasks.

State and persistence behavior: Persistent metadata/data are managed by `Garage::new` and tables created by bootstrap. `initial_config` can write cluster layout, imported access keys, buckets, aliases, and bucket-key permissions. Runtime state includes worker tasks, server tasks, watch cancellation, metrics exporter, tracing provider, and RPC handlers.

Dependencies and integration points: It integrates configuration, background task scheduling, RPC system run loop, S3/K2V/Admin/Web API crates, model tables, layout manager, bucket/key helpers, metrics, and tracing setup. It is the daemon side exercised by all integration tests in `garage/tests`.

Risks: Single-node bootstrap refuses non-replication-factor-1 configs, existing multi-node knowledge, and layout versions greater than one, so operational flags can prevent startup. Default access key/bucket setup depends on environment variables and existing table state. Server task errors are logged after join, but the daemon continues shutdown. K2V config without a K2V-enabled build only logs an error.

Test signals: Integration harness startup validates server launch, layout application, API binding, Admin JSON API, S3, Web, and optional K2V paths. Specific tests exercise default runtime surfaces: bucket/key metadata, website config, S3 object operations, and K2V table behavior.
