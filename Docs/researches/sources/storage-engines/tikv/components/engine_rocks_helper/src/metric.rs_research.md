<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/metric.rs -->
# sources/storage-engines/tikv/components/engine_rocks_helper/src/metric.rs

## Purpose
`metric.rs` registers Prometheus metrics for RocksDB damaged SST recovery bookkeeping.

## Important APIs, Types, and Functions
`TIKV_ROCKSDB_DAMAGED_FILES` is an `IntGauge` tracking damaged SST files waiting for recovery. `TIKV_ROCKSDB_DAMAGED_FILES_DELETED` is an `IntCounter` tracking damaged SST files deleted by recovery.

## Control Flow
The metrics are registered lazily through `lazy_static!`. Callers increment, set, or read them directly.

## State and Persistence Behavior
The state is process-local Prometheus metric state. It is not persisted across restarts.

## Dependencies and Integration Points
`sst_recovery.rs` increments the gauge when a damaged file overlaps live regions, sets it after timeout checks, and increments the delete counter when an obsolete damaged file is removed.

## Risks and Edge Cases
Metric registration uses `unwrap`, so duplicate registration names would panic. Gauge correctness depends on all mutation paths in recovery keeping it synchronized with `damaged_files`.

## Test Signals
Recovery tests indirectly exercise the gauge increment path. Additional tests could assert metric values around deletion and timeout paths, but global Prometheus metrics can make tests order-sensitive.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/metric.rs -->
