# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheValue.java

## Purpose

`CacheValue<VALUE>` stores a cached table value or delete tombstone together with an epoch used for cache cleanup. The complete 57-line source was read for this report.

## Important APIs, Types, and Functions

Static factories are `get(long epoch, V value)` for non-null values and `get(long epoch)` for null tombstones. Getters are `getCacheValue` and `getEpoch`.

## Control Flow

The value factory rejects null; the tombstone factory intentionally creates a null-valued cache entry. Cache cleanup compares epochs to remove flushed entries.

## State and Persistence Behavior

It is in-memory state reflecting table cache entries. Epochs typically correspond to Ratis transaction log indices and are used to decide when cached entries can be evicted after persistence.

## Dependencies and Integration Points

It depends on `Objects` and is used across `Table`, `TypedTable`, and all cache implementations.

## Risks and Edge Cases

Null value is overloaded to mean deletion/tombstone, so code must use the correct factory. The class has no `equals`, so `CacheResult.equals` compares values by object identity unless `CacheValue` instances are the same.

## Test Signals

Tests should cover null rejection, tombstone creation, epoch-based cleanup behavior, and callers correctly interpreting null as deletion.
