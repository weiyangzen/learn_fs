<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs

### Purpose
Emits timeout and progress metrics and defines a summary struct for operation timeout/stall/success/failure rates.

### Important APIs, Types, And Functions
Exports `record_timeout_event`, `record_operation_duration`, `record_dynamic_timeout`, `record_operation_progress`, `record_stalled_operation`, `record_operation_completion`, and `TimeoutMetricsSummary`. The summary stores total operations, timed out, stalled, successful, and failed counts with timeout/stall/success rate helpers.

### Control Flow
Recorders emit counters, gauges, and histograms. Dynamic timeout records size and timeout gauges plus a size histogram. Completion records success/failure through a status label. Summary rate methods return zero when total operations is zero.

### State And Persistence
No recorder state. Summary is plain caller-owned memory.

### Dependencies And Integration Points
Pairs with `io-core/src/timeout_wrapper.rs` but does not depend on it directly. Re-exported from `lib.rs`.

### Risks
Operation labels are dynamic strings and can be high cardinality if callers include IDs or paths. `record_dynamic_timeout` records a size histogram but not a timeout histogram, only a timeout gauge, so historical timeout distribution may be incomplete depending on backend behavior.

### Test Signals
Tests execute all recorders and validate summary rate calculations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs -->
