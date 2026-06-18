<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs

### Purpose
Provides a singleton `Arc<PerformanceMetrics>` for process-wide shared performance counters.

### Important APIs, Types, And Functions
`GLOBAL_PERFORMANCE_METRICS` is a `OnceLock<Arc<PerformanceMetrics>>`. `get_global_metrics` initializes it with `PerformanceMetrics::new()` on first access and returns a cloned `Arc`.

### Control Flow
Callers invoke `get_global_metrics`; `OnceLock::get_or_init` lazily creates the singleton, and `clone` increments the `Arc` reference count.

### State And Persistence
State is global and process-local. Counter values persist for the lifetime of the process and cannot be reset through this module's public API.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, `Arc`, and `OnceLock`. Integrates with any component that needs shared counters without passing a metrics object explicitly, and with `MetricsCollector` for global collection.

### Risks
Global mutable metric state can make tests order-dependent. The tests assert lower bounds after prior writes for some counters, acknowledging cross-test persistence. No reset API exists outside direct access to atomic fields.

### Test Signals
Tests verify pointer identity across calls, recording visibility through the singleton, and collector updates through one `Arc` being visible through another.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs -->
