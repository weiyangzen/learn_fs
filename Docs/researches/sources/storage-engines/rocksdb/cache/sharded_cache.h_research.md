# sources/storage-engines/rocksdb/cache/sharded_cache.h

## Purpose
This header defines the generic sharded-cache framework used by RocksDB cache implementations. It separates non-template shared configuration from the template `ShardedCache<CacheShard>` adapter that maps public `Cache` operations to per-shard implementations.

## Important APIs, Types, And Functions
`CacheShardBase` documents the shard concept and provides defaults for metadata policy, hash type, hash computation, sharding hash extraction, and printable options. `ShardedCacheBase` declares shared public methods for IDs, capacity, strict limit, secondary-cache default accessors, printable options, hash seed, and shard geometry. `ShardedCache<CacheShard>` owns a cache-line-aligned shard array and implements `SetCapacity()`, `SetStrictCapacityLimit()`, `Insert()`, `CreateStandalone()`, `Lookup()`, `Erase()`, `Release()`, `Ref()`, usage/occupancy/table-address aggregation, `ApplyToAllEntries()`, `EraseUnRefEntries()`, `DisownData()`, and shard initialization/destruction helpers.

## Control Flow
Public operations compute a shard hash using `CacheShard::ComputeHash(key, hash_seed_)`, pick a shard with `HashPieceForSharding(hash) & shard_mask_`, and delegate to that shard. Capacity and strict-limit changes lock `config_mutex_`, update shared configuration, and apply per-shard updates. `ApplyToAllEntries()` rotates through shards with per-shard iteration states to limit lock hold time. The derived cache constructor must call `InitShards()` exactly once to placement-new each shard and enable destructor cleanup.

## State And Persistence Behavior
The template owns aligned shard memory and a boolean indicating whether shard destructors should run. Shared state in `ShardedCacheBase` is volatile cache configuration. `DisownData()` can intentionally leak shard data when heap allocations do not need freeing, avoiding shutdown-time destruction cost in supported builds.

## Dependencies And Integration Points
The header depends on `rocksdb/advanced_cache.h`, hash utilities, port alignment allocation, and mutex utilities. `LRUCache` derives from `ShardedCache<LRUCacheShard>`, and HyperClock cache types follow the same concept. Public cache factory options rely on this layer for sharding behavior.

## Risks And Edge Cases
The template assumes each shard implements the documented concept exactly; signature drift can produce difficult template errors. `ApplyToAllEntries()` currently clamps `average_entries_per_lock` with `std::min(aepl, 1)`, meaning it will use at most one average entry per lock regardless of a larger request, which is a behavior worth checking if iteration performance is changed. The aligned shard allocation must be paired with explicit shard destructor calls only after successful `InitShards()`.

## Test Signals
LRU tests validate shard operations through one-shard construction and public `NewCache()` wrappers. HyperClock tests stress sharded table sizing, capacity limits, and occupancy. Secondary-cache tests with `num_shard_bits=2` validate multi-shard async lookup and common cache-key prefix handling.
