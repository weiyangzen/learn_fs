# sources/storage-engines/rocksdb/db/db_block_cache_test.cc

## Purpose

`db_block_cache_test.cc` is a RocksDB gtest suite for the block-based table block cache contract. It exercises cache insertion, lookup, eviction, strict capacity behavior, pinning, entry-role statistics, cache warming during flush and compaction, compression dictionary blocks, secondary cache type coverage, cache key stability, and cache-key encoding. The file is not production code; it is an integration-heavy regression suite that drives `DBTestBase` through real DB opens, flushes, compactions, external file ingestion, checkpoints, and iterator reads while observing `Statistics`, cache occupancy, and block cache internals.

The tests intentionally cover several block roles: data blocks, index blocks, filter blocks, filter/index metadata partitions, compression dictionary blocks, write-buffer dummy entries charged through cache, and cache-entry stats collector entries. They also verify behavior across LRU and HyperClock cache implementations, partitioned and unpartitioned metadata, runtime options, and cache keys based on SST unique IDs.

## Important APIs, Types, and Helpers

The main fixture is `DBBlockCacheTest : DBTestBase`. It provides `GetTableOptions()` with a tiny `block_size` so each key-value pair tends to occupy its own data block, `GetOptions()` wiring statistics and a block-based table factory, `InitTable()` for a fixed ten-key data set, and counter helpers around `BLOCK_CACHE_*` and `BLOCK_CACHE_COMPRESSION_DICT_*` tickers. `GetCacheEntryRoleCountsBg()` reads `DB::Properties::kFastBlockCacheEntryStats` and parses role counts through `BlockCacheEntryStatsMapKeys`.

Custom cache/test adapters are central to the suite:

- `PersistentCacheFromCache` implements `PersistentCache` backed by a regular typed cache for compressed persistent-cache coverage when Snappy is enabled.
- `ReadOnlyCacheWrapper` rejects block cache inserts.
- `PriorityTrackingCache` records `Cache::Priority` for cache warming inserts.
- `MockCache` subclasses `LRUCache` and counts high/low priority inserts.
- `LookupLiarCache` wraps a cache and can force a particular lookup to return not found, simulating a race where an insert becomes redundant.
- `StableCacheKeyTestFS` disables file unique IDs and hard links so cache key stability can be tested through copied/checkpointed DBs using table properties.
- `CacheKeyTest` constructs synthetic `TableProperties`, calls `BlockBasedTable::SetupBaseCacheKey()` / `BlockBasedTable::GetCacheKey()`, and uses local decoding helpers to validate the 128-bit cache-key encoding.
- `DBBlockCachePinningTest` parameterizes partitioned metadata and three `PinningTier` knobs: top-level index, partition blocks, and unpartitioned metadata.

The suite depends on RocksDB internals from `cache/*`, `table/block_based/*`, `db/db_impl/*`, `table/unique_id_impl.h`, `env/unique_id_gen.h`, fault injection FS wrappers, and sync points. It also uses `Checkpoint`, `SstFileWriter`, `ExportImportFilesMetaData`, `WriteBufferManager`, `DB::GetMapProperty`, and direct cache APIs such as `Insert`, `Lookup`, `EraseUnRefEntries`, `ApplyToAllEntries`, `SetCapacity`, `SetStrictCapacityLimit`, `GetUsage`, `GetPinnedUsage`, and `GetOccupancyCount`.

## Control Flow and Test Coverage

The early tests validate basic data-block cache lifecycle. `IteratorBlockCacheUsage` opens an iterator with `fill_cache=false`, seeks into a table, observes nonzero usage while the iterator pins a block, then verifies usage returns to zero after delete. `TestWithoutCompressedBlockCache` fills an empty-capacity LRU cache with pinned iterator blocks, shrinks capacity to current usage, enables strict capacity, and verifies the next seek fails with `MemoryLimit` and increments add-failure stats. After releasing pinned iterators, subsequent reads hit the cache without inserts.

`IndexAndFilterBlocksOfNewTableAddedToCache` and `IndexAndFilterBlocksStats` validate eager caching of index/filter blocks after table creation when `cache_index_and_filter_blocks` and Bloom filters are enabled. They assert index/filter miss and add counters after flush, then prove later `KeyMayExist` and `Get` calls hit cached metadata. The stats variant checks byte insertion counters and cache usage for metadata blocks.

The cache warming tests cover `BlockBasedTableOptions::prepopulate_block_cache`. `WarmCacheWithDataBlocksDuringFlush` verifies flush-only warming adds data blocks and avoids read misses, while compaction does not add more under flush-only settings. `WarmCacheWithDataBlocksDuringCompaction` uses `PriorityTrackingCache` and `kFlushAndCompaction`: flush inserts are low priority, compaction output data blocks are inserted at bottom priority, and reads after compaction miss no data blocks. `DBBlockCacheTest1.WarmCacheWithBlocksDuringFlush` parameterizes full filters versus partitioned filters and verifies data, index, filter, and compression dictionary related cache stats during flush warming, including the doubled metadata counts for partitioned filter/index layouts.

`DynamicOptions` changes the block-based table factory string at runtime to switch `prepopulate_block_cache` among `kFlushOnly`, `kDisable`, and `kFlushAndCompaction`. It demonstrates that new flushes observe the updated option while existing data remains readable; the test documents unsupported dynamic cache replacement cases as commented-out expected failures.

Priority and paranoia coverage follows. `IndexAndFilterBlocksCachePriority` checks `cache_index_and_filter_blocks_with_high_priority`; index/filter blocks respect the configured priority while data blocks remain low priority. `ParanoidFileChecks` verifies that with `paranoid_file_checks=true`, table creation/compaction reads data blocks and populates cache, and that disabling the option dynamically stops those additional cache inserts.

`CacheCompressionDict` iterates block-based format versions 6 and 7 and every supported compression. For compression algorithms that support dictionaries, bottommost compaction creates dictionary blocks, preloads them, and later reads hit the cached dictionary plus index while only the data block is missed/inserted. Unsupported dictionary compressions must still avoid crashes/corruption.

`CacheEntryRoleStats` is a large role-accounting integration test over partitioned/unpartitioned metadata and LRU/HyperClock caches. It clears cache entries except the stats collector, performs misses and hits that load filters, index blocks, data blocks, and write buffer reservations, then validates `kFastBlockCacheEntryStats` and `kBlockCacheEntryStats`. It uses mock time to check background versus foreground refresh intervals, simulates a long scan to stretch refresh timing, confirms a pinned stats collector survives a full cache, and injects DB mutex lock/unlock during cache scans to check the scan path is not holding the DB mutex.

`HyperClockCacheReportProblems` fills a HyperClock cache with fake entries at expected, smaller, and larger than estimated sizes. It captures info-log messages via `CountingLogger` to verify periodic stats report no warnings in normal range, warnings/errors when the configured estimated value size is too small, and info/warning when it is too high.

`DBBlockCacheTypeTest` runs against all testing cache types from `secondary_cache_test_util`. `AddRedundantStats` uses `LookupLiarCache` to create redundant index, filter, and data block insert attempts and validates per-role redundant add counters plus aggregate `BLOCK_CACHE_ADD_REDUNDANT`. `Uncache` parameterizes partitioned metadata and `options.uncache_aggressiveness`. It proves obsolete blocks are removed after non-trivial compaction when aggressiveness is nonzero, preserved when disabled, preserved across reopen without cache churn, and not incorrectly uncached on trivial move compactions.

The cache key tests validate persistence and encoding invariants. `StableCacheKeys` runs with and without original file numbers in table properties. It creates ordinary SSTs, external ingested SSTs, exports a column family, reopens, copies via checkpoint, imports into a different DB, and re-ingests external files. When original file numbers are present, cache stats show stable key reuse across these operations; when missing, stats intentionally grow because cache key reuse is unsafe. `DBImplSessionIdStructure` checks generated session IDs share high bits in a process and differ in low counter bits. `CacheKeyTest.Encodings` constructs a base key and brute-forces many combinations of session counter bits, file number bits, and offset bits whose total fits in 128 bits. The local decoder reconstructs all original fields, validating the uniqueness claim in `cache_key.cc`.

`DBBlockCachePinningTest.TwoLevelDB`, compiled with LZ4, builds an L0 and L1 file with enough metadata to partition index/filter blocks and with an L1 compression dictionary. It erases unpinned blocks and then reads from L0 and L1, computing expected metadata/dictionary misses from the selected `PinningTier` settings. The test distinguishes `kNone`, `kFlushedAndSimilar`, and `kAll`, and treats compaction-created L1 metadata differently from flush-created L0 metadata.

## State and Persistence Behavior

The suite repeatedly persists state to SST files through `Flush()`, moves files through `CompactRange()`, imports/exports files, and reopens DBs with different options. The important persistent state under test is not user values but table metadata: filter/index blocks, compression dictionary blocks, table properties such as `orig_file_number`, DB/session IDs, external SST unique IDs, and block-based table format versions. Cache contents are process-local and intentionally survive `Reopen(options)` when the same cache object is reused; several tests assert this persistence of in-memory cache state across DB close/open, while also verifying obsolete-file cache entries are dropped after compaction when configured.

The cache-key path is especially persistence-sensitive. Stable cache keys are derived from table properties and internalized SST unique IDs so identical SST files in checkpoints, exports, imports, and external ingestion can reuse cache entries. The control case with missing file numbers proves the implementation degrades safely by avoiding reuse rather than risking collision.

## Dependencies and Integration Points

These tests integrate with block-based table readers/builders, Bloom filter metadata, compression dictionary training, compaction, flush, table cache, secondary cache type factories, checkpoint/export/import flows, external SST ingestion, cache-entry statistics collectors, `Statistics` tickers, `PerfContext` indirectly through reads, `SyncPoint` injection, and the mocked environment clock. They also rely on compile-time feature gates: Snappy for persistent compressed-cache helper coverage, Linux/Windows for warming tests under one block, and LZ4 for dictionary/pinning tests.

## Risks and Edge Cases

The file protects against regressions in cache accounting, redundant insertion races, strict-capacity failure handling, iterator pin lifetime, stale cache stats, DB mutex deadlocks during cache scans, incorrect cache priority, accidental compaction cache warming, incorrect trivial-move uncaching, compression dictionary cache misses/corruption, and cache key collisions across DB copies/imports. A notable risk in this suite is tight coupling to exact ticker increments and cache occupancy. Changes in table metadata layout, filter partitioning, cache metadata charging, or compaction file layout can require careful test updates even when user-visible behavior is still correct.

## Test Signals

The strongest signals are exact `Statistics` ticker assertions for `BLOCK_CACHE_*`, `BLOCK_CACHE_INDEX_*`, `BLOCK_CACHE_FILTER_*`, `BLOCK_CACHE_DATA_*`, compression dictionary counters, redundant add counters, cache entry role counts, and byte insertion counters. Cache object signals include `GetUsage`, `GetPinnedUsage`, `GetOccupancyCount`, `EraseUnRefEntries`, `ApplyToAllEntries`, and insert priority observations. Behavioral signals include `Get`, `KeyMayExist`, iterator validity/status, compaction level counts, no cache churn after reopen, log severity counts for HyperClock cache warnings, and stable cache stats across checkpoint/export/import workflows.
