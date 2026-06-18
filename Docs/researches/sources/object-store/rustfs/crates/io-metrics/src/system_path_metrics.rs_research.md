<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs

### Purpose
Records failures involving system paths, categorized by path kind, operation, and reason.

### Important APIs, Types, And Functions
Exports `record_system_path_failure(path_kind, operation, reason)`.

### Control Flow
The function increments `rustfs_system_path_failures_total` with the three static labels.

### State And Persistence
No local state; aggregation is external via the metrics recorder.

### Dependencies And Integration Points
Re-exported from `lib.rs` and intended for code that interacts with OS paths, directories, or files where failures should be visible in system metrics.

### Risks
The labels are `&'static str`, which encourages low cardinality. Callers must still define a stable vocabulary. There are no tests in this file.

### Test Signals
No local unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs -->
