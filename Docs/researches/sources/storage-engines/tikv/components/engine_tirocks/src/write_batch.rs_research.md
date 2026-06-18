# sources/storage-engines/tikv/components/engine_tirocks/src/write_batch.rs

Purpose: Implements engine-trait write batches for TiRocks, including multi-batch splitting for large TiKV writes.

Important APIs and control flow: `WriteBatchExt for RocksEngine` creates `RocksWriteBatchVec`. `RocksWriteBatchVec` holds the engine, a vector of TiRocks `WriteBatch` instances, save-point indexes, and the active batch index. `check_switch_batch` starts a new sub-batch when multi-batch writing is enabled and the active batch reaches 16 keys. `write_opt` chooses `write_multi` or single `write`; `should_write_to_engine` uses either batch-count or total-count thresholds. `Mutable` methods resolve default/CF handles and append put/delete/range-delete commands.

State, persistence, and dependencies: Batched commands are in memory until `write_opt` persists them through TiRocks with translated write options. Save points track only the sub-batch index stack and clear later sub-batches during rollback.

Integration points, risks, and test signals: Used by TiKV apply/write paths and shared write-batch tests. Risks include atomicity assumptions around multi-batch writes, save-point behavior across sub-batches, memory retention after large batches, merging batches with different split boundaries, and no memtable insert hint support. Tests verify flush thresholds in pipeline and multi-batch modes, persisted writes, clear behavior, and merge count/sub-batch shape.
