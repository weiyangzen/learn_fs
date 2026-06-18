<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/write_batch.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/write_batch.rs

## Purpose
`write_batch.rs` implements `engine_traits::WriteBatch` for RocksDB using either a single RocksDB `WriteBatch` or a vector of smaller batches for RocksDB multi-batch write mode.

## Important APIs, Types, and Functions
`WriteBatchExt for RocksEngine` exposes `write_batch`, `write_batch_with_cap`, and `WRITE_BATCH_MAX_KEYS`. `RocksWriteBatchVec` stores the `Arc<DB>`, vector of raw batches, save-point batch indices, active index, per-batch key limit, and whether multi-batch write is supported.

`check_switch_batch` advances to a new raw batch when multi-batch mode is enabled and the current batch reaches `WRITE_BATCH_MAX_KEY_NUM`. `write_impl` calls either `multi_batch_write_callback` over active batches or `write_callback` on the first batch. Trait methods implement size/count/empty/write/clear/savepoint/rollback/merge. `Mutable` methods add put/delete/range-delete operations with optional CF handles.

## Control Flow
New write batches start with one raw batch. Each mutation calls `check_switch_batch` before adding the operation. `should_write_to_engine` uses active batch count in multi-batch mode and total key threshold in single-batch mode. Savepoints record the current raw batch index and delegate RocksDB savepoint state to that raw batch. Rollback clears later raw batches, resets the index, and rolls back the selected raw batch.

## State and Persistence Behavior
Before `write_opt`, operations are buffered in memory. `write_opt` persists them atomically through RocksDB according to the write options and selected write mode. `clear` reuses allocation but can shrink overly large raw-batch vectors.

## Dependencies and Integration Points
It depends on RocksDB `Writable`, `WriteBatch`, write callbacks, `RocksWriteOptions`, CF handle lookup, and `engine_traits::{Mutable, WriteBatch, WriteBatchExt}`. The engine-level multi-batch support flag comes from `RocksEngine::support_multi_batch_write`.

## Risks and Edge Cases
`is_empty` checks only the first raw batch; under normal switching an operation exists in the first batch before later batches, but unusual clear/merge paths should preserve that invariant. `count` estimates earlier batches as `index * batch_size_limit` plus current count, which assumes all earlier batches are full. Savepoint semantics span multiple raw batches only by clearing later batches and rolling back the recorded one. Callback for empty multi-batch writes is noted as not called.

## Test Signals
Tests cover `should_write_to_engine` thresholds under pipeline and multi-batch modes, successful writes, and `clear`. More tests should cover savepoint rollback across batch boundaries, `merge`, CF operations, and empty write callback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/write_batch.rs -->
