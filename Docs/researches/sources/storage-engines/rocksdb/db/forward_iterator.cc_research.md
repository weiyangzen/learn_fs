# sources/storage-engines/rocksdb/db/forward_iterator.cc

Implements `ForwardIterator`, a forward-only/tailing internal iterator optimized for `Seek()` and `Next()` over the mutable memtable, immutable memtables, L0 files, and sorted higher levels. It avoids reseeking immutable sources while moving forward, refreshes on SuperVersion changes, handles upper-bound trimming, async IO retry seeks, pinning, and SuperVersion cleanup.

The file defines `ForwardLevelIterator`, an `InternalIterator` over non-overlapping files in one level. `ForwardIterator` implements `SeekToFirst()`, `Seek()`, `Next()`, `Valid()`, key/value/write-time accessors, `status()`, `PrepareValue()`, property lookup, pinning APIs, and `TEST_CheckDeletedIters()`. Helpers rebuild/renew iterators, reset incomplete children, seek internal sources, select current source, decide whether immutable sources need seeking, delete trimmed iterators, find a file by range, and release SuperVersions immediately or through `PinnedIteratorsManager`.

`Seek()`/`SeekToFirst()` refresh or renew iterators when the SuperVersion changes, reset incomplete iterators, then call `SeekInternal()`. `SeekInternal()` seeks mutable state, may rebuild the immutable heap, trims iterators outside `iterate_upper_bound`, and runs a second pass for async IO `TryAgain`. `Next()` advances the current child, updates the cached previous-key interval when moving through immutable data, may reseek the mutable iterator, pushes valid immutable children back into the heap, and calls `UpdateCurrent()`.

Runtime state includes a referenced `SuperVersion`, arena-owned memtable iterators, heap-managed immutable iterators, table-cache iterators for L0, `ForwardLevelIterator`s for L1+, current pointer, cached previous internal key, aggregate immutable status, upper-bound trim flags, pinning manager, and arena storage. There is no persistent state.

Dependencies include `DBImpl`, `ColumnFamilyData`, SuperVersion lifecycle, memtable iterators, `VersionStorageInfo`, table cache, range tombstone aggregation, prefix extractors, async IO feature checks, and pinned cleanup. Range tombstones are unsupported unless ignored.

Risks: cached interval invariants can cause skipped data or extra seeks if wrong; range tombstones force `NotSupported`; upper-bound trimming deletes child iterators and relies on later rebuilds; SuperVersion renewal reuses L0 iterators by file pointer identity; async IO status propagation is subtle. Test signals are sync points, `TEST_CheckDeletedIters()`, broader iterator tests, and `forward_iterator_bench.cc`.
