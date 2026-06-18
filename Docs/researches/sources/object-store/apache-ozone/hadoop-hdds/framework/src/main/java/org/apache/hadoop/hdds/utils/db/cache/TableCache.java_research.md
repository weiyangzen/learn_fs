# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableCache.java

## Purpose

`TableCache` defines the cache contract for RocksDB-backed Ozone metadata tables. The complete 121-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `get`, `loadInitial`, `put`, `cleanup`, `evictCache`, `size`, `iterator`, `lookup`, `getEpochEntries`, `getStats`, and `getCacheType`. It defines `MAY_EXIST` and enum `CacheType` with `FULL_CACHE`, `PARTIAL_CACHE`, and `NO_CACHE`.

## Control Flow

Implementations use `lookup` to distinguish definitive hit, definitive absence, and uncertain absence. `cleanup` removes entries matching persisted epochs depending on implementation and cleanup policy.

## State and Persistence Behavior

The interface owns no state. Implementations hold in-memory cache entries and use epochs to coordinate with persistence to RocksDB/Ratis-applied state.

## Dependencies and Integration Points

It uses `CacheKey`, `CacheValue`, `CacheResult`, `CacheStats`, and Java collection types. `TypedTable` consumes the interface to make cache decisions.

## Risks and Edge Cases

The raw static `MAY_EXIST` singleton requires unchecked casts in implementations. The contract assumes callers understand full versus partial cache semantics. Cleanup behavior depends on externally supplied epoch lists.

## Test Signals

Tests should be implementation contract tests for lookup statuses, cleanup semantics, metrics, and cache type reporting across full, partial, and no-cache implementations.
