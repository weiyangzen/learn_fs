<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/performance.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/performance.rs

### Purpose
Defines `PerformanceMetrics`, a thread-safe atomic counter bundle for cache, I/O, concurrency, latency, and error counters.

### Important APIs, Types, And Functions
Fields include cache hits/misses/L1/L2, bytes read/written, disk read/write counts, average/P95/P99 latency in microseconds, current/peak concurrent requests, total errors, timeout errors, and disk errors. Methods include `new`, `cache_hit_rate`, `l1_hit_rate`, cache recorders, byte/disk recorders, `update_concurrent_requests`, and error recorders. `Default` delegates to `new`.

### Control Flow
Recording methods perform relaxed atomic increments or stores. L1/L2 hit methods increment tier-specific counter and total hit. `update_concurrent_requests` stores current count and uses a CAS loop to update peak only when the new count exceeds prior peak. Timeout and disk error methods increment specific counters and total error.

### State And Persistence
All state is process-local atomics in the struct. There is no reset method and no persistence. Cloning is not implemented; sharing is expected through `Arc<PerformanceMetrics>`.

### Dependencies And Integration Points
Used by `MetricsCollector`, `AutoTuner`, `global_metrics`, benchmarks, and public API consumers. It is the advanced in-process counterpart to metrics macro emission.

### Risks
Relaxed atomics are appropriate for telemetry but not for strict ordering. Rates can be transiently inconsistent under concurrent updates. No saturation guards exist for counters, though `u64` overflow is unlikely in normal operation. L1 hit rate divides L1 hits by total hits, not total cache lookups.

### Test Signals
Tests cover zero initialization, cache hit rate, L1 hit rate, I/O byte/count recording, concurrent current/peak tracking, and timeout/disk error totals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/performance.rs -->
