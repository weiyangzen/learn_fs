<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs

### Purpose
Emits metrics for lock optimization, spin behavior, lock hold/contention, early release, and object namespace lock diagnostics.

### Important APIs, Types, And Functions
Exports `record_lock_optimization_enabled`, `record_spin_attempt`, `record_spin_count_change`, `record_lock_hold_time`, `record_early_release`, `record_contention_event`, `record_object_lock_diag_enabled`, `record_object_lock_diag_acquire_duration`, `record_object_lock_diag_hold_duration`, `record_object_lock_diag_slow_acquire`, and `record_object_lock_diag_slow_hold`. `LockMetricsSummary` stores acquisition/release/spin/early/contention counts and computes spin success and contention rates.

### Control Flow
Simple lock metrics emit gauges, counters, or histograms. Object lock diagnostic helpers use static `op` and `mode` labels for acquire/hold duration and slow-event counters. Summary methods compute rates defensively returning zero for empty denominators.

### State And Persistence
No local recorder state. `LockMetricsSummary` is caller-owned in-memory data.

### Dependencies And Integration Points
Uses `metrics` and `Duration`. Re-exported by `lib.rs`, and likely used by namespace lock and lock optimization code.

### Risks
Generic `record_contention_event` and deadlock module `record_lock_contention` use related names but different label behavior, which can confuse dashboards. Object diagnostic labels are `&'static str`, which is good for cardinality if call sites use constants. Summary does not update from recorder functions automatically.

### Test Signals
Tests execute all helpers. Several tests install a local recorder to verify object lock diagnostic gauge, histograms, and counters are registered with expected names. Summary rate calculations are validated.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs -->
