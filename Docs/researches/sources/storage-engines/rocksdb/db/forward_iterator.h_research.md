# sources/storage-engines/rocksdb/db/forward_iterator.h

Declares `ForwardIterator`, a forward-only `InternalIterator` intended as a faster tailing-style iterator by keeping direct access to DB, SuperVersion, memtable, and file iterators. It supports `Seek()`, `SeekToFirst()`, and `Next()`. `Prev()`, `SeekForPrev()`, and `SeekToLast()` are explicitly unsupported and set `NotSupported`.

`MinIterComparator` and `MinIterHeap` provide the heap used to merge immutable sources. The constructor takes `DBImpl`, `ReadOptions`, `ColumnFamilyData`, optional current `SuperVersion`, and an `allow_unprepared_value` flag. Public overrides expose validity, key/value, write time, status, `PrepareValue()`, iterator property retrieval, pinning, and test-only deleted-iterator accounting.

Private helpers cover cleanup and SuperVersion release, iterator rebuild/renewal, level iterator construction, incomplete iterator reset, seeking, current-source selection, immutable seek avoidance, file-range binary search, upper-bound checks, child pinning propagation, and deletion through pinning-aware paths. Members hold DB/CF pointers, read options, comparator/prefix extractor pointers, current SuperVersion, mutable/immutable/L0/level child iterators, min heap, current pointer, validity/status flags, cached previous key, pinning manager, and arena.

Dependencies are RocksDB iterator/table internals, `Arena`, comparators, DB read options, version storage declarations, and SuperVersion-owned options. Integration is with DB iterator creation for forward/tailing reads.

Risks are subset semantics and raw-lifetime complexity: callers needing reverse movement are unsupported, child iterator and SuperVersion ownership is manual, and prefix extractor state participates in seek-avoidance correctness. Test signals include `TEST_CheckDeletedIters()`, sync-point tests in iterator suites, and benchmark pressure from `forward_iterator_bench.cc`.
