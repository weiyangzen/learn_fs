# sources/object-store/rustfs/crates/obs/src/telemetry/dial9.rs

## Purpose
Integrates `dial9_tokio_telemetry` with RustFS runtime construction, including environment-driven configuration, trace output directory validation, rotating writer setup, and session guard handling.

## Important APIs, Types, and Functions
`Dial9Config` stores enabled state, output directory, file prefix, max file size, rotation count, optional S3 settings, and sampling rate. `Dial9Config::from_env()` reads `rustfs_config` environment keys via `rustfs_utils` helpers and clamps sampling rate. `base_path()` combines output directory and prefix. `Dial9SessionGuard` wraps an optional `TelemetryGuard`, validates setup in `new()`, exposes `is_active()`, `shutdown()`, and `set_guard()`. Module functions `init_session()`, `is_enabled()`, and `build_traced_runtime()` provide the public flow.

## Control Flow
If disabled, `new()` logs a disabled state and returns `Ok(None)`. If enabled, it creates the output directory asynchronously and falls back to disabled on directory creation failure. `build_traced_runtime()` is synchronous runtime-building code: it rejects disabled mode, reloads config, creates the output directory, constructs a `RotatingWriter` with total rotation budget, and wraps a Tokio builder with `TracedRuntime::builder().with_task_tracking(true)`.

## State and Persistence
Trace data is persisted to rotating files under `output_dir` with `file_prefix`. The guard keeps the underlying telemetry guard alive so drop can flush. S3 fields are parsed but reserved for future use in this implementation.

## Dependencies and Integration Points
Depends on `dial9_tokio_telemetry`, `rustfs_config`, `rustfs_utils`, Tokio, and the crate's `TelemetryError`. It is intended to be called by the runtime builder and broader telemetry initialization.

## Risks
`init_session()` only validates directory setup; the actual active guard is attached later through runtime construction. `build_traced_runtime()` errors when disabled, so callers must check `is_enabled()`. Sampling and S3 settings are currently parsed but not passed to the dial9 library. File-size multiplication by rotation count should be watched for extreme env values.

## Test Signals
Tests cover default config values, base path construction, and default disabled detection when the environment variable is absent. Additional tests could cover clamping, env parsing, and runtime writer failure paths.
