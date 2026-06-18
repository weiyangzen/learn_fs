# sources/storage-engines/rocksdb/cache/lru_cache.h

## Purpose
This header declares the internal LRU cache structures used by RocksDB's sharded cache framework. It defines the handle state machine, custom hash table, per-shard cache API, and the `LRUCache` public wrapper class.

## Important APIs, Types, And Functions
`LRUHandle` extends `Cache::Handle` and stores object pointer, helper, hash-chain link, LRU-list links, charge, key, hash, refs, and flags. It provides `Ref()`, `Unref()`, `HasRefs()`, cache/pool/priority predicates, flag setters, `Free()`, metadata-charge calculation, and charge access. `LRUHandleTable` declares lookup/insert/remove and ranged iteration. `LRUCacheShard` declares the shard operations expected by `ShardedCache`: `ComputeHash()`, `Insert()`, `CreateStandalone()`, `Lookup()`, `Release()`, `Ref()`, `Erase()`, capacity and strict-limit setters, usage/occupancy queries, partial iteration, and `EraseUnRefEntries()`. `LRUCache` derives from `ShardedCache<LRUCacheShard>` and exposes public `Cache` overrides.

## Control Flow
The header documents three handle states: externally referenced and in cache; unreferenced and in cache/LRU; externally referenced and detached from cache. Public methods move handles among these states: lookup moves unreferenced cache entries out of LRU and increments refs, release may return entries to LRU or free them, erase/overwriting detaches entries from the hash table, and insert may evict older LRU entries before installing a new one.

## State And Persistence Behavior
The declared state is volatile cache metadata. `LRUCacheShard` owns capacity, high/low pool ratios and cached pool capacities, a circular dummy LRU head, boundary pointers for low and bottom priority pools, `LRUHandleTable`, usage counters, a `DMutex`, and an eviction callback reference. The header explicitly separates frequently and infrequently modified fields to reduce false sharing.

## Dependencies And Integration Points
The header depends on `cache/sharded_cache.h`, port alignment/malloc helpers, `util/autovector.h`, and `util/distributed_mutex.h`. It is consumed by `lru_cache.cc`, tests, and factory code. Type aliases expose `LRUCache`, `LRUHandle`, and `LRUCacheShard` in `ROCKSDB_NAMESPACE` for callers and tests.

## Risks And Edge Cases
The main risk is violating handle/list invariants: `key_data` must remain the last field, `Free()` requires `refs == 0` and a valid helper, and metadata-charge calculation depends on allocator support. The mutable/immutable flag split relies on callers only changing immutable flags during single-threaded setup. The shard API is not independently thread-safe unless operations use its mutex as implemented in the `.cc`.

## Test Signals
Tests access `TEST_GetLRUList()`, `TEST_GetLRUSize()`, and priority predicates on `LRUHandle` to assert exact list order and pool membership. Secondary-cache tests indirectly validate that public aliases and `LRUCacheOptions` produce usable cache instances compatible with block-cache helpers.
