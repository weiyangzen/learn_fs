# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/FullTableCache.java

## Purpose

`FullTableCache` is the cache implementation whose in-memory state mirrors the entire table. It supports sorted iteration and definitive negative lookups. The complete 233-line source was read for this report.

## Important APIs, Types, and Functions

It implements `TableCache<KEY,VALUE>`. Important members are a `ConcurrentSkipListMap` cache, epoch-to-key map, scheduled cleanup executor, cleanup queue, read/write lock, and `CacheStatsRecorder`. Methods include `get`, `loadInitial`, `put`, `cleanup`, `evictCache`, `lookup`, `iterator`, `size`, `getEpochEntries`, `getStats`, and `getCacheType`.

## Control Flow

Startup calls `loadInitial` to fill cache without epoch tracking. Runtime `put` stores values or tombstones; only tombstones are added to epoch cleanup tracking. `cleanup` replaces the cleanup queue with requested epochs; a scheduled task wakes every second, drains queued epochs, and calls `evictCache`. `lookup` returns `EXISTS` for non-null entries and `NOT_EXIST` for missing entries or tombstones.

## State and Persistence Behavior

State is in-memory and intended to match persistent RocksDB state plus recent tombstones. Cleanup removes tombstones once epochs have been persisted. It does not write storage itself.

## Dependencies and Integration Points

It depends on Guava `ThreadFactoryBuilder`, concurrent collections, locks, and table cache value/result wrappers. `TypedTable` uses it when `CacheType.FULL_CACHE` is requested and initializes it from RocksDB.

## Risks and Edge Cases

Because misses are definitive, cache initialization and update ordering must be correct. The cache uses `CacheKey.compareTo`, so key string ordering/collisions affect storage. Cleanup queue `clear` means a newer cleanup call replaces pending epochs. `evictCache` assumes the epoch list is non-empty and sorted enough for the last element to be a high-water mark. The scheduled executor is not exposed for shutdown here.

## Test Signals

Tests should cover initial load, definitive miss semantics, tombstone lookup, epoch cleanup ordering, concurrent put/cleanup, sorted iteration, stats, and executor cleanup behavior in lifecycle tests.
