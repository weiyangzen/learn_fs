<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/config.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/config.rs

### Purpose
Defines a unified, crate-local configuration surface for cache, I/O scheduler, backpressure, timeout, and deadlock-detection settings.

### Important APIs, Types, And Functions
Constants define default cache capacity/TTL/memory, scheduler concurrency/priority thresholds/buffer bounds, backpressure watermarks, lock timeout, deadlock interval, and buffer sizes. `CacheSettings`, `IoSchedulerSettings`, `BackpressureSettings`, `TimeoutSettings`, `DeadlockDetectionSettings`, and `IoConfig` provide defaults and builder methods. Behavior helpers include backpressure `high_threshold`/`low_threshold` and timeout `timeout_with_backoff`.

### Control Flow
Defaults assemble the configuration graph. Builder methods consume and return modified structs. Backpressure thresholds multiply max capacity by watermark percentages. Retry timeout multiplies default timeout by `retry_backoff_factor.powi(retry_count)`.

### State And Persistence
Configuration is plain in-memory data. There is no config file parsing or persistence.

### Dependencies And Integration Points
Uses `Duration`. Publicly re-exported from `lib.rs`. Overlaps conceptually with `io-core::config::IoSchedulerConfig` and `cache_config::CacheConfig`, making it a high-level metrics crate configuration facade rather than the only runtime config source.

### Risks
There is no validation for watermarks ordering, buffer min/base/max ordering, retry factor bounds, or zero concurrency. Because these settings duplicate ideas from other modules, drift can occur between `IoSchedulerSettings`, `CacheSettings`, and runtime config types. `timeout_with_backoff` can grow very large for high retry counts.

### Test Signals
Tests cover cache and scheduler builders, backpressure threshold math, retry backoff for first and second retry, and unified config composition.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/config.rs -->
