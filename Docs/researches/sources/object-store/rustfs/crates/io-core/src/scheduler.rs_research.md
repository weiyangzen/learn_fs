<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/scheduler.rs -->
## sources/object-store/rustfs/crates/io-core/src/scheduler.rs

### Purpose
Implements adaptive I/O scheduling primitives for RustFS `io-core`: priority classification, load-level classification, bandwidth tiering, strategy selection, and buffer-size heuristics. The scheduler decides per-request buffer sizes, readahead enablement, priority, and pressure flags from file size, permit wait time, access style, active request count, and optional storage profile.

### Important APIs, Types, And Functions
`IoPriority` classifies requests as `High`, `Normal`, or `Low` from size thresholds and provides metric-friendly labels. `IoLoadLevel` maps wait duration into `Low`, `Medium`, `High`, or `Critical`. `BandwidthTier` classifies bytes/sec. `IoStrategy` is the decision output: buffer size, flags, current concurrency, optional bandwidth, load, priority, and booleans explaining why buffers were expanded, reduced, or throttled. `IoScheduler` owns `IoSchedulerConfig`, an atomic `active_requests`, and mutex-protected `IoLoadMetrics`. Its main APIs are `calculate_strategy`, `calculate_multi_factor_strategy`, `record_wait_time`, and `load_metrics`. Standalone helpers include `get_concurrency_aware_buffer_size`, `get_advanced_buffer_size`, `get_buffer_size_for_media`, and `calculate_optimal_buffer_size`. `IoSchedulingContext` is a builder-style data carrier for multi-factor scheduling inputs.

### Control Flow
`calculate_strategy` loads active request count, derives priority from file size, derives load from permit wait thresholds, multiplies base buffer size by concurrency, load, and sequential-access factors, clamps by configured min/max, and returns a filled `IoStrategy`. `calculate_multi_factor_strategy` starts from that result and applies storage-media factors, sequential boost, random-access penalty, and profile readahead preference. The standalone helpers layer similarly: file-size short-circuit, basic concurrency adjustment, access-pattern boost/penalty, media adjustment, load multiplier, and final clamping.

### State And Persistence
All state is process-local and in-memory. Active request count is an `AtomicUsize`; load samples are accumulated in a mutex-held `IoLoadMetrics`. There is no persistence across process restarts. `record_wait_time` silently skips updates if the mutex is poisoned or unavailable.

### Dependencies And Integration Points
Uses `IoSchedulerConfig` plus `io_profile::{AccessPattern, StorageMedia, StorageProfile}` from `io-core`. Decision fields and labels are designed to integrate with `rustfs-io-metrics` scheduler metrics, though this file does not emit metrics directly.

### Risks
`IoPriority::from_size` casts `i64` to `usize`, so negative unknown sizes can become huge and classify as low priority. `decrement_requests` uses `fetch_sub` without saturation, so an unbalanced decrement can underflow. The standalone `get_concurrency_aware_buffer_size` hardcodes `concurrent_requests = 1`, which means callers of that helper do not receive real concurrency pressure. The mutex fallback in `load_metrics` can mask poisoned state by returning defaults.

### Test Signals
Unit tests cover priority classification, load classification, bandwidth tiering, scheduler strategy under basic concurrency, load metrics averaging, buffer helpers, media adjustment, optimal sizing, and scheduling-context builder fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/scheduler.rs -->
