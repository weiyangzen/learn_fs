<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/error.rs -->
# sources/object-store/rustfs/crates/obs/src/error.rs

## Purpose
Defines observability error types used by global initialization and telemetry backend setup.

## Important APIs, Types, and Functions
`GlobalError` wraps failures such as setting the global metrics recorder, setting the global guard, missing guard initialization, metrics/system errors, PID/process/core-count/GPU errors, log-send failure, timeout, and telemetry initialization. `TelemetryError` captures exporter build failures, metrics recorder install failure, subscriber init failure, I/O errors, and permission errors. `From<std::io::Error>` maps I/O into `TelemetryError::Io`.

## Control Flow
There is no active control flow except `From` conversions and `thiserror` formatting. `#[from]` conversions allow `?` propagation from underlying setup functions.

## State and Persistence
No state or persistence. Errors carry strings and source error conversions.

## Dependencies and Integration
Depends on `thiserror`, `metrics::SetRecorderError`, Tokio `SetError`, `Arc<Mutex<OtelGuard>>`, and the crate `Recorder`. Used by `global.rs` and telemetry initialization modules.

## Risks
Several variants store only `String`, losing typed source errors and backtrace context. `SendFailed` and `Timeout` use static strings, so callers need external context for detailed diagnostics.

## Test Signals
No direct tests. Compile-time use in `global.rs` tests and telemetry initialization paths validates conversion compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/error.rs -->
