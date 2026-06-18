# sources/storage-engines/rocksdb/table/compaction_merging_iterator.cc

Purpose: implements a compaction-specific merging iterator that merges point-key child iterators with range tombstone start keys. Its goal is to preserve sorted output while exposing tombstone starts so compaction partitioning can avoid oversized overlap ranges.

Important APIs/types/functions: `CompactionMergingIterator` implements `SeekToFirst`, `Seek`, `Next`, `key`, `value`, `status`, bound checks, pinned iterator propagation, and `IsDeleteRangeSentinelKey`. Private structures include `HeapItem`, `CompactionHeapItemComparator`, a binary min-heap, range tombstone iterator storage, and pinned tombstone heap items. Factory `NewCompactionMergingIterator` constructs heap or arena instances.

Control flow: seeking clears the heap, positions all point iterators, adds valid ones, positions each `TruncatedRangeDelIterator`, inserts current tombstone starts, skips file-boundary sentinel keys, and selects the heap top. `Next` advances either the current point iterator or current range tombstone iterator, restores the heap, skips sentinels, and updates `current_`.

State and persistence: no persistent writes. Runtime state owns child iterator wrappers, range tombstone iterators, pinned heap items, dummy tombstone value, heap, accumulated status, and optional internal stats count of running compaction sorted runs. Destruction decrements stats and deletes child iterators respecting arena mode.

Dependencies/integration: depends on internal key comparator, `TruncatedRangeDelIterator`, `IteratorWrapper`, `BinaryHeap`, pinned iterator manager, and `InternalStats`. Level iterators can receive pointers to their associated range tombstone iterator through the second element of the input pairs.

Risks and test signals: risks include comparator ordering between tombstone starts and file boundary sentinels, ignoring parse failures in `Seek`, status propagation, and assuming range tombstones from a file are exhausted before skipping its sentinel. No direct tests in this subset; compaction tests elsewhere should cover behavior.
