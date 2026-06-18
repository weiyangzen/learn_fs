# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.h

Purpose: defines persistent-cache configuration and the abstract tiering model for volatile and persistent storage tiers.

Important APIs/types: `PersistentCacheConfig` carries `Env`, clock, path, logger, direct IO flags, cache/file/write-buffer sizes, writer queue depth, pipelining controls, dispatch size, and compression mode. `ValidateSettings()` enforces non-null path/env, cache/file/buffer sizing, queue depth, and dispatch alignment. `PersistentCacheTier` extends `PersistentCache` with lifecycle, reserve/erase, recursive stats, next-tier chaining, and `TEST_Flush`. `PersistentTieredCache` presents a chain of tiers as one cache.

Control flow and state: concrete tiers implement `Insert`, `Lookup`, `IsCompressed`, and options printing. Tier chains pass misses/evictions downward depending on concrete behavior. `write_buffer_count()` computes enough slabs based on writer depth and cache file size to avoid pipeline deadlock.

Dependencies and integration: included by all persistent-cache tier implementations and exposed through RocksDB table options via `PersistentCache`.

Risks and test signals: validation catches several deadlock-prone configurations, but the unused `MakePersistentCacheConfig` declaration has no implementation in this file set. The tiered cache API expects at least one tier and asserts otherwise. Header comments contain typos but document intended RAM/NVM/SSD tiering.
