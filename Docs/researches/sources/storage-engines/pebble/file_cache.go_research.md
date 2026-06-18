# sources/storage-engines/pebble/file_cache.go

## Purpose
Implements Pebble's shared open-file cache for SSTable and blob readers, plus the DB-specific handle that creates point/range iterators, supplies blob/value-block readers, tracks iterator leaks, and reports file-cache metrics.

## Important APIs, Types, And Functions
Important types include `FileCacheMetrics`, `tableNewIters`, `fileCacheHandle`, `FileCache`, `fileCacheKey`, `fileCacheValue`, `tableCacheShardReaderProvider`, `iterSet`, and `iterKinds`. Key functions include `NewFileCache`, `FileCache.Ref/Unref`, `fileCacheHandle.newHandle`, `Close`, `openFile`, `findOrCreateTable`, `findOrCreateBlob`, `Evict`, `Metrics`, `withReader`, `GetValueReader`, `newIters`, `newPointIter`, `SetupBlobReaderProvider`, `newRangeDelIter`, `newRangeKeyIter`, and `getTableProperties`.

## Control Flow
`NewFileCache` initializes a sharded generic cache with an init function that opens object-storage files and constructs either an `sstable.Reader` or `blob.FileReader`, and a release function that closes readers and decrements counts. A DB creates a handle with object provider, block cache handle, reader options, and corruption callback. Iterator construction finds or creates the table reader, installs corruption reporting in read env, applies virtual/shared-ingest transforms, creates requested range-key, range-deletion, and point iterators, and pins the cache value until the point iterator close hook runs.

## State And Persistence Behavior
The cache holds process-local reader objects, refcounts, per-type counts, iterator counts, race-build stack traces for leaked refs, block-cache file entries, and per-handle filter metrics. It does not persist data, but it controls access to persisted SSTable/blob files and must evict block-cache state when files are evicted.

## Dependencies And Integration Points
Integrates with object storage, block cache, generic cache, manifest table metadata, virtual SSTables, value separation, blob readers, range deletion/key span iterators, compaction iterators, block property filters, IO tracing, and corruption reporting from `event.go`.

## Risks And Edge Cases
Reference ownership is subtle: point iterators pin cache values, range iterators generally do not, and value-block/blob reader providers hold their own refs. Leaked iterators make handle close fail and can panic on eviction. Virtual metadata must be initialized before reads. Shared ingested SSTables with synthetic seqnums hide obsolete points. Range-key filtering is disabled when range-key deletions exist to avoid surfacing deleted lower-level keys.

## Test Signals
Signals are broad and indirect through iterator, compaction, value-separation, corruption, excise size-estimation, and file-cache tests. Metrics (`Size`, `TableCount`, `BlobFileCount`, hits, misses), iterator leak errors, and corruption callbacks are important runtime indicators.
