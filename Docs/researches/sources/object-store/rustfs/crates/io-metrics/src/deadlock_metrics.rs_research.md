<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs

### Purpose
Records metrics related to potential deadlocks, long-held locks, lock acquisition/release/contention, and wait-graph edge changes.

### Important APIs, Types, And Functions
Exports `record_deadlock_detected`, `record_long_held_lock`, `record_lock_acquisition`, `record_lock_release`, `record_lock_contention`, `record_wait_edge_added`, and `record_wait_edge_removed`.

### Control Flow
Functions emit counters and histograms through `metrics`. Deadlock detection records total and cycle length. Long-held lock records count and hold duration, ignoring the lock id parameter. Lock acquisition/release/contention record by caller-supplied lock type. Wait-edge helpers increment add/remove counters.

### State And Persistence
No local state. External metrics backend owns retention and aggregation.

### Dependencies And Integration Points
Designed for lock tracking and deadlock detection components. Re-exported from `lib.rs`, while `config.rs` defines deadlock detection settings.

### Risks
`record_long_held_lock` accepts but ignores `_lock_id`, so per-lock diagnosis must happen elsewhere. Dynamic `lock_type` labels can be high cardinality if not constrained. The module records observations only; it does not detect deadlocks or maintain a wait graph.

### Test Signals
Tests execute all recording functions for representative values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs -->
