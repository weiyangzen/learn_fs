<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.cc -->
# sources/storage-engines/rocksdb/table/merging_iterator.cc

Purpose: Implements RocksDB's internal merging iterator for combining multiple child `InternalIterator`s into one sorted stream, with optional range tombstone awareness. It is the core fan-in iterator used above memtables/SST iterators and can skip point keys covered by range deletions.

Important APIs and functions: Defines `MergingIterator`, `NewMergingIterator()`, and `MergeIteratorBuilder` implementation. Public iterator methods include `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `PrepareValue`, `SetPinnedItersMgr`, `SetRangeDelReadSeqno`, and `Prepare`. Internal helpers maintain min/max heaps and range tombstone state: `SeekImpl`, `SeekForPrevImpl`, `FindNextVisibleKey`, `FindPrevVisibleKey`, `SkipNextDeleted`, `SkipPrevDeleted`, `SwitchToForward`, `SwitchToBackward`, `InsertRangeTombstoneToMinHeap`, and `InsertRangeTombstoneToMaxHeap`.

Control flow: Forward scans build `minHeap_` from child iterators and range tombstone endpoints, pop tombstone starts into `active_`, and skip heap-top points covered by active tombstones. Reverse scans lazily initialize `maxHeap_`, mirror the endpoint logic, and treat tombstone ends as activation points. Seeks can cascade: when a newer range tombstone covers the target, older levels are reseeked to the tombstone end or start to avoid scanning invisible keys. Direction switches reseek non-current children around the current key, rebuild the appropriate heap, and reposition range tombstone iterators.

State and persistence: Runtime state includes `children_`, `pinned_heap_item_`, `range_tombstone_iters_`, `active_`, `current_`, `direction_`, heap instances, accumulated `status_`, pinned iterator manager, prefix seek mode, arena ownership mode, and optional `iterate_upper_bound_`. There is no durable persistence; correctness depends on preserving heap/range-deletion invariants across every iterator call.

Dependencies and integration points: Depends on `InternalKeyComparator`, `IteratorWrapper`, `TruncatedRangeDelIterator`, `ArenaWrappedDBIter`, `BinaryHeap`, perf counters, async `TryAgain` statuses, and file-boundary sentinel behavior from level iterators. Builder integration updates `LevelIterator` range tombstone pointers and DB iterator memtable range tombstone pointer storage.

Risks: Range tombstone logic is highly invariant-sensitive, especially same-level sequence checks, endpoint op-type ordering, file-boundary sentinels, upper-bound filtering, and reverse cascading seek. Async `TryAgain` paths must replay the exact target used before prefetch. Arena mode changes destruction responsibility. Prefix seek mode relaxes one direction-switch assertion and can hide ordering assumptions.

Test signals: Exercise forward/reverse merge order, duplicate internal keys, direction switches, async child iterators, pinned key/value forwarding, empty/one/many children, range tombstones across levels, same-level tombstone sequence comparisons, tombstones spanning file boundaries, upper-bound-limited iteration, prefix seek mode, and builder single-iterator fast paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.cc -->
