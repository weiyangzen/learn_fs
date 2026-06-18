# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/PartialTableCache.java

## Purpose

`PartialTableCache` stores only recent or pending table entries and tombstones, so misses are not definitive and must fall back to RocksDB. The complete 189-line source was read for this report.

## Important APIs, Types, and Functions

It implements `TableCache<KEY,VALUE>` with a `ConcurrentHashMap` cache, epoch-to-key `ConcurrentSkipListMap`, single-thread cleanup executor, and `CacheStatsRecorder`. Methods mirror `FullTableCache`: `get`, `put`, `cleanup`, `evictCache`, `lookup`, `iterator`, `size`, `getEpochEntries`, `getStats`, and `getCacheType`.

## Control Flow

`loadInitial` is intentionally a no-op. `put` stores entries and tracks all entries by epoch. `cleanup` asynchronously executes `evictCache`, which scans epochs up to the supplied last epoch and removes entries whose current cache epoch still matches. `lookup` returns `MAY_EXIST` on misses, `EXISTS` for values, and `NOT_EXIST` for tombstones.

## State and Persistence Behavior

State is transient and represents mutations not yet cleaned after DB flush. Cleanup removes entries once epochs are safe. Persistent state remains in RocksDB.

## Dependencies and Integration Points

It integrates with `TypedTable` for `CacheType.PARTIAL_CACHE` and relies on higher-level Ozone locks around same-key updates, as described in comments.

## Risks and Edge Cases

`epochEntries` stores mutable `HashSet`s inside a concurrent map; concurrent writes to the same epoch set can race. Cleanup assumes the epoch list is non-empty and that the last element is the cutoff. The executor is not exposed for shutdown. Misses must never be treated as absence by callers.

## Test Signals

Tests should cover MAY_EXIST miss behavior, tombstones, epoch cleanup with overwritten entries, concurrent updates around cleanup, stats, and fallback-to-RocksDB behavior through `TypedTable`.
