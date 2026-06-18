# sources/storage-engines/rocksdb/cache/lru_cache.cc

## Purpose
This file implements RocksDB's sharded LRU cache shard, handle hash table, and `LRUCacheOptions` factories. It is the concrete implementation behind `NewLRUCache()`/`LRUCacheOptions::MakeSharedCache()` and can optionally be wrapped by `CacheWithSecondaryAdapter` when a secondary cache is configured.

## Important APIs, Types, And Functions
`LRUHandleTable` implements a compact bucketed hash table with `Lookup()`, `Insert()`, `Remove()`, `FindPointer()`, and `Resize()`, indexing by upper hash bits because lower bits are used for sharding. `LRUCacheShard` implements capacity changes, insertion, lookup, ref/release, erase, LRU-list maintenance, priority pools, standalone handle creation, usage queries, and iteration. `LRUCache` adapts shard internals to the public `Cache` API and exposes handle value/charge/helper access. `LRUCacheOptions::MakeSharedCache()` validates option ratios, picks default shard bits, constructs `LRUCache`, and wraps it with `CacheWithSecondaryAdapter` when `secondary_cache` is set.

## Control Flow
Insertion allocates an `LRUHandle`, sets priority and in-cache flags, evicts LRU entries until there is room, and inserts the handle into the hash table. If the caller does not request a handle, the entry is placed on the LRU list immediately; otherwise it is pinned by an external ref. Lookup removes an unreferenced cache entry from the LRU list, increments `refs`, and marks it hit. Release decrements refs; the last referenced in-cache entry either returns to the priority-partitioned LRU list, is erased when over capacity or requested, or is freed if no longer in cache. Erase removes from the table and frees immediately only when there are no external refs. Capacity and pool-ratio changes trigger eviction or pool rebalancing under the shard mutex.

## State And Persistence Behavior
State is in-memory only. `usage_` tracks charged cache bytes, `lru_usage_` tracks bytes currently evictable on the LRU list, and pinned usage is `usage_ - lru_usage_`. `high_pri_pool_usage_` and `low_pri_pool_usage_` track priority-reserved portions. Each `LRUHandle` carries value, helper, hash, key bytes, total charge, refs, mutable cache/list flags, and immutable priority/standalone flags. There is no disk persistence, but eviction callbacks can transfer ownership to secondary-cache adapters.

## Dependencies And Integration Points
The implementation depends on `cache/sharded_cache.h`, `cache/secondary_cache_adapter.h`, `monitoring/perf_context_imp.h`, `monitoring/statistics_impl.h`, `util/distributed_mutex.h`, allocator metadata helpers, and RocksDB `Cache` helper callbacks. `LRUCacheShard` is a template parameter to `ShardedCache<LRUCacheShard>`. Eviction callbacks are installed by the cache wrapper and are the handoff point for secondary-cache demotion.

## Risks And Edge Cases
The code has tight invariants around `refs`, `M_IN_CACHE`, list membership, and usage accounting. Incorrect pool pointer updates can corrupt priority pools, especially when capacity shrinks and entries overflow from high to low to bottom priority pools. Strict capacity behavior differs depending on whether the caller requested a handle. `CreateStandalone()` can return uncharged handles when strict capacity would otherwise reject them, so callers must treat standalone handles differently from cache-resident entries. Eviction callback ownership is subtle: if it takes ownership, the handle is freed without calling the normal value deleter.

## Test Signals
`lru_cache_test.cc` directly validates LRU ordering, high/low/bottom priority pool behavior, capacity reduction, and insertion after shrinking capacity. Secondary-cache tests validate the factory path where `LRUCacheOptions::MakeSharedCache()` wraps LRU in `CacheWithSecondaryAdapter`. Compressed-secondary tests also exercise eviction callbacks through primary-cache demotion.
