# sources/storage-engines/rocksdb/cache/sharded_cache.cc

## Purpose
This file implements the non-template portions of RocksDB's sharded cache base. It handles hash-seed selection, capacity and strict-limit configuration storage, shard-count helpers, printable options, and default shard-bit selection.

## Important APIs, Types, And Functions
`DetermineSeed()` chooses a 31-bit cache hash seed from an explicit option, host name, or quasi-random process-unique generator. `ShardedCacheBase` implements `ComputePerShardCapacity()`, `GetPerShardCapacity()`, `NewId()`, `GetCapacity()`, default secondary-cache capacity/pinned usage accessors, `HasStrictCapacityLimit()`, `GetUsage(Handle*)`, and `GetPrintableOptions()`. `GetDefaultCacheShardBits()` chooses up to six shard bits based on capacity and a minimum shard size. `GetNumShardBits()` and `GetNumShards()` expose sharding geometry.

## Control Flow
Construction computes `shard_mask_` from `num_shard_bits`, chooses `hash_seed_`, stores strict capacity and total capacity, and initializes the ID counter. Capacity reads and strict-limit reads take `config_mutex_`; template-derived classes update those fields and then fan out per-shard changes. Printable options snapshot shared configuration under the same mutex and append subclass-specific options.

## State And Persistence Behavior
State is in-memory cache configuration: atomic `last_id_`, immutable shard mask and hash seed, and mutex-protected `strict_capacity_limit_` and `capacity_`. There is no persistence. `NewId()` provides monotonically increasing IDs for cache clients during the cache lifetime.

## Dependencies And Integration Points
The file depends on environment hostname lookup, unique ID generation, hash utilities, math helpers, and mutex utilities. It supports both `LRUCache` and HyperClock cache implementations through the template layer in `sharded_cache.h`.

## Risks And Edge Cases
Hash seed selection must remain bounded to 31 bits so users can reproduce diagnostics. Hostname lookup failure falls back to process-stable generated data. Per-shard capacity rounds up, so total shard capacity can exceed configured capacity by up to `num_shards - 1`. Default shard bits are capped at six to avoid over-sharding small or large caches.

## Test Signals
LRU and HyperClock tests indirectly validate shard capacity, strict-limit behavior, printable options, and table sizing. Tests using `NewCache()` with specific `num_shard_bits` validate that cache keys distribute correctly and async secondary-cache lookup works over multiple shards.
