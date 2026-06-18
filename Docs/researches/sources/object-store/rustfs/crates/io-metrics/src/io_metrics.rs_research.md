<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs

### Purpose
Provides focused metrics helpers and a small in-memory summary struct for I/O scheduler decisions, priorities, load changes, bandwidth observations, buffer adjustments, queue operations, and starvation.

### Important APIs, Types, And Functions
Exports `record_io_scheduler_decision`, `record_io_priority_decision`, `record_load_level_change`, `record_bandwidth_observation`, `record_buffer_size_adjustment`, `record_queue_operation`, `record_starvation_event`, and `IoSchedulerStats`.

### Control Flow
Recording functions emit counters, gauges, and histograms with labels for load level, strategy, priority, reason, operation, and queue priority. `IoSchedulerStats` has mutating methods that increment local counters and `reset`.

### State And Persistence
Metric helper functions store no state. `IoSchedulerStats` is a plain mutable summary; it is not atomic or synchronized and persists only as long as the caller retains it.

### Dependencies And Integration Points
Used by `lib.rs` re-exports and intended to pair with `io-core/src/scheduler.rs` decision outputs. Metrics names are specific to scheduler telemetry.

### Risks
Dynamic label strings can cause high-cardinality series if callers pass unconstrained reasons or priorities. There is overlap with top-level `lib.rs` functions like `record_io_strategy`, `record_io_load_level`, and `record_permit_wait`, so consumers need a consistent naming plan.

### Test Signals
Tests execute each recorder and validate `IoSchedulerStats` counter increments.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs -->
