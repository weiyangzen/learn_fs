<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/collector.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/collector.rs

### Purpose
Provides an async `MetricsCollector` that updates `PerformanceMetrics`, records transfer metrics, and computes latency average/P95/P99 over a bounded sliding window.

### Important APIs, Types, And Functions
`MetricsCollector` stores an `Arc<PerformanceMetrics>`, a Tokio `RwLock<VecDeque<Duration>>` of latency samples, and `max_latency_samples`. Public APIs are `new`, `with_default_max_samples`, async `record_io_operation`, async `sample_count`, and `max_samples`.

### Control Flow
`record_io_operation` updates bytes and operation counters based on `is_read`, emits `record_data_transfer`, pushes duration into the sample window, pops the oldest sample if over limit, then calls `update_latency_percentiles`. Percentile update reads samples, copies microsecond values into a vector, sorts it, computes arithmetic average as the "avg" latency, stores avg/P95/P99 into `PerformanceMetrics`, and emits corresponding top-level metrics.

### State And Persistence
Latency samples are in-memory and bounded. Underlying counters are atomics in `PerformanceMetrics`. No persistence exists across process restarts.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, Tokio `RwLock`, `VecDeque`, and top-level metric functions in `lib.rs`. It is used by benchmarks and global metrics tests.

### Risks
Every recorded operation sorts the entire retained window, which is O(n log n) and may be expensive on hot paths with large windows. P95/P99 index calculation uses `len * percentile` floored and then clamped, which is simple but not a statistically nuanced quantile estimator. `duration.as_millis() as f64` can record `0` for sub-millisecond transfers in `record_data_transfer`, suppressing transfer bandwidth calculation.

### Test Signals
Async tests cover construction, read/write counter updates, sample count, average/P95/P99 updates, sample retention limit, and read/write distinction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/collector.rs -->
