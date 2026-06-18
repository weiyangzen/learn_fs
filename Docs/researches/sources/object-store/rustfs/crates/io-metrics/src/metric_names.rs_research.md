<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs

### Purpose
Provides stable metric-name constants for zero-copy-related telemetry.

### Important APIs, Types, And Functions
The `zero_copy` module defines constants for buffer operation totals/bytes, memory copy totals/bytes, shared reference operations, BufReader layers eliminated and buffer sizes, Direct I/O operations/bytes, average copy count, throughput MB/s, and current memory saved bytes.

### Control Flow
No runtime control flow. Constants are referenced by `lib.rs` zero-copy extension functions.

### State And Persistence
No state.

### Dependencies And Integration Points
Used by top-level `record_zero_copy_buffer_operation`, `record_memory_copy`, `record_shared_ref_operation`, `record_bufreader_optimization`, `record_direct_io_operation`, and `update_zero_copy_performance_metrics`.

### Risks
Only zero-copy names are centralized here; many other metric names remain inline across modules. Renaming constants would affect dashboards. No compile-time relationship exists between these constants and external metric descriptors.

### Test Signals
`lib.rs` zero-copy tests assert selected constants are non-empty.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs -->
