# sources/storage-engines/rocksdb/table/two_level_iterator.cc

Purpose: implements `NewTwoLevelIterator()` by defining `TwoLevelIndexIterator`, an `InternalIteratorBase<IndexValue>` that flattens a first-level partition index into the concatenated stream of second-level block/index entries. It is RocksDB's partitioned-index traversal helper: the first-level iterator yields `IndexValue` handles, and `TwoLevelIteratorState::NewSecondaryIterator()` materializes the iterator for the selected partition.

Important APIs and control flow: `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, and `Prev` all position the first-level iterator, call `InitDataBlock()`, then position or advance the second-level iterator. `SkipEmptyDataBlocksForward()` and `SkipEmptyDataBlocksBackward()` loop across partitions whose secondary iterator is null or exhausted without error. `status()` prioritizes first-level errors, then second-level errors, then the iterator's saved corruption status.

State and ownership: the object owns `state_`, `first_level_iter_`, and the current `second_level_iter_`; destruction deletes all three through non-arena paths. `data_block_handle_` caches the handle used for the active secondary iterator so `InitDataBlock()` can avoid recreating it when the partition offset has not changed and the existing iterator is not incomplete. No persistent state is written.

Dependencies and integration: depends on RocksDB internal iterator wrappers, `BlockHandle`, `IndexValue`, and table/block format code. The state object is supplied by block-based table code and hides the details of reading partitioned index blocks.

Risks and test signals: the code assumes iterators are not arena-created, so ownership mismatches would cause invalid deletes. `InitDataBlock()` only compares handle offset, so callers must not present distinct partitions with the same offset but different semantics. A null secondary iterator becomes `Corruption("Missing block for partition ...")`. Boundary tests should cover empty first-level indexes, empty partitions, backward seeks before/after range ends, incomplete secondary iterators, and status precedence.
