<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs

### Purpose
Centralizes metrics emission for capacity cache, capacity refresh, scan, timeout fallback, symlink, and dirty-disk behavior.

### Important APIs, Types, And Functions
Exports recorders for cache hit/miss/served, current capacity bytes, update completion/failure, refresh requests/joiners/inflight/results/scope, dirty disk count, write operations, symlink sizes, timeout fallback/stall/dynamic timeout, scan sampling, scan mode, and per-disk scan statistics.

### Control Flow
Each function emits counters, gauges, and/or histograms with labels such as source, mode, result, scope, disk, and estimated. `record_capacity_update_completed` records completion count, duration, bytes, and estimated flag. `record_capacity_scan_disk` emits multiple per-disk histograms and optionally increments partial-error counter.

### State And Persistence
No local state. Aggregation is external through the metrics recorder.

### Dependencies And Integration Points
Uses `metrics::{counter,gauge,histogram}` and `Duration`. Intended for storage-capacity management code that caches disk usage, refreshes capacity, and scans filesystem contents.

### Risks
The `disk` label is caller-provided and can be high cardinality if it includes unstable paths, UUIDs, or transient mount names. Several labels are `&'static str`, which encourages bounded vocabularies for source/mode/result/scope. Histograms for bytes and file counts can be high-volume during large scans.

### Test Signals
No unit tests in this file. Compile coverage comes from crate tests that use exported functions elsewhere, but these specific helpers are not individually asserted here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs -->
