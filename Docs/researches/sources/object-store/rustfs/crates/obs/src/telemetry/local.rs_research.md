# sources/object-store/rustfs/crates/obs/src/telemetry/local.rs

## Purpose
Implements local logging initialization for stdout-only and rolling-file modes, including JSON formatting, request-id promotion, optional stdout mirroring, directory hardening, fallback behavior, and background log cleanup.

## Important APIs, Types, and Functions
`RequestIdJsonFormat<T>` wraps the JSON formatter to add top-level `request_id` and `request-id` fields from the active span scope. `span_scope_request_id()` scans formatted span fields from root to current span. `build_json_log_layer()` creates a JSON tracing layer with RFC3339 time, target, thread, file/line, current span, span list, and optional span events. `init_local_logging()` chooses file or stdout mode. `init_stdout_only()` registers stdout JSON logging. `init_file_logging_internal()` prepares rolling files, optional stdout mirror, and cleanup. `ensure_dir_permissions()` tightens Unix permissions to 0755. `should_fallback_to_stdout()`, `format_file_logging_fallback_warning()`, and `emit_file_logging_fallback_warning()` handle recoverable file setup failures. `spawn_cleanup_task()` builds a `LogCleaner` and periodically runs it in `spawn_blocking`.

## Control Flow
If no log directory is configured, initialization immediately installs stdout JSON logging and returns an `OtelGuard` with a stdout worker guard. If a log directory is configured, file setup creates the directory, tightens permissions, selects rotation, opens a size-capped `RollingAppender`, installs file and optional stdout layers, then starts cleanup. Permission-like file setup failures fall back to stdout; other errors are returned. Cleanup loops on a Tokio interval and records success/failure counters.

## State and Persistence
In file mode, logs persist as rolling files in the configured directory. Cleanup persists side effects by deleting/compressing old files according to config. Runtime state is held by `OtelGuard`: worker guards and cleanup task handle. The module also toggles observability metric enablement and increments startup/cleanup counters.

## Dependencies and Integration Points
Depends on `OtelConfig`, `OtelGuard`, `LogCleaner`, rolling appender, `build_env_filter`, `metrics`, `tracing_subscriber`, `tracing_appender`, `serde_json`, Tokio, and `rustfs_config` defaults. It is a central local backend for crate telemetry initialization.

## Risks
`tracing_subscriber::init()` can only be called once per process, so tests and callers must avoid double initialization. Request-id extraction depends on JSON-formatted span fields; malformed fields skip promotion. File fallback only handles permission-like errors, while invalid filenames and other setup failures return errors. Cleanup interval defaults and file matching must align with rolling filename format to avoid deleting active logs.

## Test Signals
Tests cover invalid filename errors without panic, permission-denied fallback decisions, actionable fallback warning messages, parseable ANSI-free JSON logs, stable JSON shape across ANSI settings, request-id promotion from current span, and parent request-id promotion from nested recovery-monitor spans.
