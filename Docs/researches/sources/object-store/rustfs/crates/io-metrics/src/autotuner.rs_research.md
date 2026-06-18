<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs

### Purpose
Implements an advisory auto-tuner that reads performance metrics, maintains history, and produces tuning recommendations for cache and I/O behavior.

### Important APIs, Types, And Functions
`AutoTuner` owns `Arc<RwLock<TunerConfig>>`, `MetricsHistory`, `Arc<RwLock<TunerState>>`, and an optional `Arc<PerformanceMetrics>`. `TunerConfig` groups `CacheTunerConfig` and `IoTunerConfig`. `TuningResult` describes tuner name, action, previous/new values, and reason. Public APIs are `new`, `with_config`, `with_metrics`, and async `tune`.

### Control Flow
`tune` updates metrics history, reads config, conditionally calls `tune_cache` and `tune_io`, logs any generated recommendations, then updates state with last tune time, count, and results. Cache tuning compares current hit rate to target and threshold. I/O tuning compares average latency to target and threshold. Metrics are read from `PerformanceMetrics` when available, otherwise defaults are used.

### State And Persistence
State is in memory. Config and state are protected by Tokio `RwLock`s. History uses bounded vectors and removes from the front when over capacity. There is no persisted tuning state and no direct mutation of the actual cache or I/O scheduler.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, Tokio sync, and `tracing`. Integrates with `MetricsCollector`/global metrics only through the shared `PerformanceMetrics` reference.

### Risks
The tuner is currently advisory: it creates `TuningResult`s but does not apply changes to cache size or buffer size. Defaults have both cache and I/O tuning disabled, so `tune` mostly updates state unless enabled. `Vec::remove(0)` is O(n), acceptable for default length 100 but worth noting if enlarged. A missing metrics reference makes cache hit rate 0 and latency 10 ms, which can produce recommendations unrelated to real load.

### Test Signals
Async tests cover creation, tuning with enabled cache config, and bounded metrics-history behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs -->
