# sources/object-store/rustfs/crates/audit/src/observability.rs

## Purpose

`observability.rs` provides audit metrics, in-memory counters, metrics crate instrumentation, human-readable reports, and performance requirement validation.

## Important APIs and Types

`init_observability_metrics` registers metric descriptors once. `AuditMetrics` owns atomic counters for processed/failed events, total dispatch time, target successes/failures, config reloads, system starts, and an async `last_reset_time`. Methods record event/target/system activity, calculate EPS, average latency, error rate, target success rate, reset counters, generate reports, and validate performance. `AuditMetricsReport` and `PerformanceValidation` are report DTOs with `format` helpers. Global helpers such as `record_audit_success`, `record_target_failure`, `get_metrics_report`, `validate_performance`, and `reset_metrics` operate on a `OnceLock<Arc<AuditMetrics>>`.

## Control Flow

Constructing metrics registers descriptors. Record methods update atomics with relaxed ordering and emit `metrics` counters/histograms/gauges. Report generation reads atomics and computes derived values. Performance validation checks EPS >= 3000, average latency <= 30 ms, and error rate <= 1%, producing recommendations for failed constraints.

## State and Persistence

State is process-local and resettable: atomics plus `last_reset_time`. Metrics are also emitted to whatever global recorder the `metrics` crate has installed, but this module does not persist data itself. The global metrics singleton cannot be replaced once initialized, though counters can be reset.

## Dependencies and Integration Points

It depends on `metrics`, `const-str` for metric names, `tokio::sync::RwLock`, `OnceLock`, and `tracing`. `pipeline.rs` records dispatch and target metrics, while system/global code can record starts and config reloads. External Prometheus/exporter integration depends on the installed metrics recorder.

## Risks and Edge Cases

`record_event_failure` increments failed events but not processed events; total events are computed as processed plus failed, so naming must be understood by consumers. `dispatch_time.as_nanos() as u64/f64` can theoretically lose precision for very long durations. Relaxed atomics are fine for approximate metrics but not for strict synchronization. `PerformanceValidation::format` includes non-ASCII status symbols and bullets, which may matter for plain log consumers. EPS depends on the last reset time, so long-running idle periods can make throughput look poor.

## Test Signals

Tests should cover descriptor idempotence, success/failure counter updates, average latency/error-rate math, target success rate defaulting to 100% with no target ops, reset behavior, report formatting, performance validation thresholds, and global helper delegation.
