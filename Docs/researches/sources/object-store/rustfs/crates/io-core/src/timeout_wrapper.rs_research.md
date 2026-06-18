<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs -->
## sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs

### Purpose
Defines timeout configuration, per-operation progress tracking, timeout checks, aggregate timeout statistics, and helper functions for adaptive timeout estimation in I/O paths.

### Important APIs, Types, And Functions
`TimeoutConfig` carries base, per-MB, min/max, S3-operation-specific timeouts, and dynamic-timeout enablement. `calculate_timeout` scales base timeout by object size and clamps it. `validate` rejects inconsistent min/max/base relationships. `TimeoutError` distinguishes timeout from invalid configuration. `OperationProgress` tracks total size, processed bytes, last-update time, stale threshold, and start time; it exposes `update`, `add`, `current`, `is_stale`, `progress_percent`, `remaining`, and `transfer_rate`. `RequestTimeoutWrapper` combines config, start time, and optional progress with APIs to check elapsed/remaining/timed-out/stalled state. `TimeoutStats` tracks operation counts, timeout counts, total/max wait time, rate, average wait, and reset. `calculate_adaptive_timeout` and `estimate_bytes_per_second` support external heuristics.

### Control Flow
Dynamic timeout calculation converts bytes to MB, adds `timeout_per_mb * mb` to base, then clamps. Wrapper checks compute the applicable timeout from optional size and compare against elapsed time. Progress updates store or add bytes and refresh last-update time under a mutex. Statistics record operations by atomically adding counts and nanoseconds, with a CAS loop for max wait time. Adaptive timeout starts from historical transfer-rate estimate when available, applies recent-timeout multipliers, then clamps between 5 seconds and 10 minutes.

### State And Persistence
State is process-local. Progress uses atomics plus a mutex-held `Instant`; stats use atomics. There is no external persistence or metrics emission here.

### Dependencies And Integration Points
Uses `thiserror` for `TimeoutError`. Designed for `io-core` request wrappers and can pair with `io-metrics/src/timeout_metrics.rs` for telemetry, though this file does not call metrics macros.

### Risks
`TimeoutStats::avg_wait_time` divides by total operation count using `checked_div`; it safely returns zero for count zero. `OperationProgress::is_stale` returns false on mutex lock failure, which can hide stale work. `update` stores an absolute byte count while `add` increments; misuse can regress or double-count progress. Operation-specific timeout fields are configured but not selected by `RequestTimeoutWrapper`, which only uses base/dynamic size timeout.

### Test Signals
Tests validate timeout calculation and config errors, progress update/add/remaining behavior, wrapper timeout detection with a short sleep, timeout stats rate, and basic progress tracking.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs -->
