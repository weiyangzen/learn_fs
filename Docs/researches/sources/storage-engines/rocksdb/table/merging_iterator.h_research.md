<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.h -->
# sources/storage-engines/rocksdb/table/merging_iterator.h

Purpose: Declares the merging iterator factory and builder used to construct sorted union iterators over RocksDB internal point iterators and optional range tombstone iterators.

Important APIs and types: `NewMergingIterator()` returns an `InternalIterator` over the union of child iterators without duplicate suppression. `MergeIteratorBuilder` owns construction of either a direct single child or an arena-allocated `MergingIterator`. Its APIs are `AddIterator()`, `AddPointAndTombstoneIterator()`, `SetMemtablePruned()`, `GetArena()`, and `Finish()`. The forward declaration `MergingIterator` identifies the implementation class returned by the factory/builder.

Control flow: Callers either add only point iterators or add point/tombstone iterator pairs. The builder switches from direct single-iterator mode to merging mode when multiple point iterators or range tombstone handling are needed. `Finish()` returns the built iterator and, when requested, wires stored range tombstone iterator slots back into `LevelIterator` or `ArenaWrappedDBIter` owners.

State and persistence: The header defines builder state for `merge_iter`, `first_iter`, `use_merging_iter`, arena ownership, deferred range-deletion pointer fixups, and a `memtable_pruned_` flag. All state is transient iterator construction state.

Dependencies and integration points: Includes `db/range_del_aggregator.h`, `rocksdb/slice.h`, `table/iterator_wrapper.h`, and iterator type aliases. It is consumed by DB iterator setup, version/level iterator composition, and read paths that need range deletion filtering.

Risks: The API requires exclusive use of either point-only or point-plus-tombstone additions. Pointer-to-slot fixups are sensitive to vector reallocation, so they are intentionally delayed. Returning a child directly in the single-iterator case changes ownership and destructor expectations.

Test signals: Compile and behavior coverage for point-only merging, single child fast path, tombstone iterator pairs, level-iterator range tombstone pointer refresh, memtable-pruned DB iterator setup, and arena-backed destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.h -->
