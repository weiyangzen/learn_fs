<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs -->
## sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs

### Purpose
Criterion benchmark suite for measuring hot metrics paths: simple request-start recording, atomic concurrent-request peak updates, and async collector I/O operation recording.

### Important APIs, Types, And Functions
Defines `bench_record_get_object_request_started`, `bench_update_concurrent_requests`, and `bench_metrics_collector_record_io_operation`. Uses `criterion_group!` and `criterion_main!` to expose the benchmark group.

### Control Flow
The first benchmark repeatedly calls `record_get_object_request_started`. The second constructs a `PerformanceMetrics` and repeatedly calls `update_concurrent_requests(64)` through `black_box`. The third builds a current-thread Tokio runtime, creates a `MetricsCollector` with 256 retained latency samples, and repeatedly `block_on`s `record_io_operation(64 KiB, 250 us, read)`.

### State And Persistence
Benchmark state is local to the Criterion process. The metrics recorder, if installed externally, may receive emitted metrics; otherwise metrics macros are effectively no-op depending on global recorder setup.

### Dependencies And Integration Points
Depends on Criterion, Tokio runtime, `PerformanceMetrics`, `MetricsCollector`, and top-level recording helpers. It is integrated through Cargo's `[[bench]]` entry.

### Risks
The collector benchmark includes Tokio `block_on`, lock acquisition, sliding-window insertion, percentile sorting, atomic updates, and metrics macro overhead together, so it is useful for pipeline cost but not isolated micro-cost. The benchmark does not install a recorder, so exporter overhead is excluded.

### Test Signals
Criterion results can reveal regressions in hot recording functions and collector overhead. It complements unit tests by measuring repeated execution cost.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs -->
