# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LRUCache.java research

## Purpose

`LRUCache` is the Java wrapper for RocksDB's sharded least-recently-used cache. It is used as a block cache, row cache, or other cache dependency by table options and DB options.

## Important APIs and types

The overloaded constructors progressively expose `capacity`, `numShardBits`, `strictCapacityLimit`, `highPriPoolRatio`, and `lowPriPoolRatio`. All constructors delegate to the native `newLRUCache(...)` and then to the `Cache` superclass. Disposal calls `disposeInternalJni(handle)`.

## Control flow

Construction is the only active path: Java computes default constructor arguments and native RocksDB builds the cache. Cache operations are inherited from `Cache`; this class only selects the LRU implementation.

## State and persistence behavior

State is native cache memory behind `nativeHandle_`. It is process-local and non-persistent. Cache contents affect read latency and memory pressure but are not durable DB state.

## Dependencies and integration points

`LRUCache` extends `Cache` and is consumed by `Options`, `BlockBasedTableConfig`, `WriteBufferManager`, and memory usage utilities. Its shard and priority-pool choices integrate with native cache partitioning and high/low priority block admission.

## Risks and test signals

Risks include native memory leaks if not closed, invalid capacities or ratios surfacing only from native code, and strict-capacity insert failures changing performance. Tests should verify constructor coverage, cache property counters through DB reads, memory usage reporting, and close/dispose behavior.
