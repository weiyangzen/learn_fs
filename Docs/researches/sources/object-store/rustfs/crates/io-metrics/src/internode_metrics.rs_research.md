<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs

### Purpose
Tracks internode network and erasure-write quorum metrics, including aggregate atomic snapshots and labeled operation/backend/classification metrics.

### Important APIs, Types, And Functions
Constants define operation labels (`read_file_stream`, `put_file_stream`, `walk_dir`, gRPC read/write) and backend labels (`tcp-http`, `grpc`, `unknown`). `InternodeOperationMetricDescriptor` and `INTERNODE_OPERATION_METRICS` list expected metric names and label sets. `InternodeMetricsSnapshot` is a readout struct. `InternodeMetrics` stores atomic totals for sent/received bytes, incoming/outgoing requests, errors, dial errors, dial timing, samples, and last dial timestamp. Methods record aggregate and operation/backend-specific bytes, requests, errors, classified errors, retries, retry successes, quorum failures, dial results, snapshots, and test reset. `global_internode_metrics` returns a `LazyLock<Arc<InternodeMetrics>>`.

### Control Flow
Operation-specific methods first update aggregate counters where appropriate, then emit labeled counters. Zero-byte sent/received samples are ignored after aggregate helper checks. Dial results update total time, sample count, average-time gauge, optional error counter, and last dial Unix millis. Snapshot loads atomics and computes average dial time with checked division.

### State And Persistence
State is in process-local atomics; global instance persists for process lifetime. Metrics macro emissions are handled by the configured recorder/exporter.

### Dependencies And Integration Points
Uses `metrics`, `Arc`, `LazyLock`, atomics, `Duration`, and `SystemTime`. It is intended for internode transport layers and erasure-write paths.

### Risks
Classified error/retry/quorum methods emit counters but do not update aggregate snapshot error or retry fields, so snapshots are intentionally limited. Label constants help cardinality, but classification/stage/dominant error must remain bounded. Dial average uses relaxed atomics and a load after increment, which is acceptable for telemetry but not a transactional statistic.

### Test Signals
Tests verify snapshot values after aggregate updates, operation methods updating aggregate snapshots, metric descriptor label sets and stable names, low-cardinality constants, and classified/retry methods not affecting aggregate byte/request snapshot fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs -->
