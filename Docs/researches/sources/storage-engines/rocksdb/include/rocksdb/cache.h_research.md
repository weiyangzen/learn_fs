# sources/storage-engines/rocksdb/include/rocksdb/cache.h

## Purpose

`cache.h` is the public C++ configuration and factory surface for RocksDB caches. It defines the vocabulary for cache entry roles, shared sharded-cache options, LRU cache options, compressed secondary caches, HyperClockCache, tiered caches, and update functions. The file is intentionally option-heavy: actual cache implementations live elsewhere, while this header lets applications construct block, row, secondary, and tiered caches with stable public configuration types.

## Important APIs, Types, and Functions

`BlockCache` and `RowCache` are currently aliases for `Cache`, with comments documenting a staged future split. `CacheEntryRole` classifies cache charges into data, filter, metadata, index, write-buffer, compression dictionary, filter construction, table-reader, file-metadata, blob, blob-cache, and miscellaneous roles. `kNumCacheEntryRoles`, `GetCacheEntryRoleName`, `CacheEntryRoleSet`, and `BlockCacheEntryStatsMapKeys` support role-based statistics and property maps.

`ShardedCacheOptions` provides common state for shard-based caches: `capacity`, `num_shard_bits`, `strict_capacity_limit`, `memory_allocator`, `metadata_charge_policy`, `secondary_cache`, and expert `hash_seed`. The hash seed constants distinguish quasi-random and host-derived behavior, addressing correlation hazards across hosts and restarts.

`LRUCacheOptions` extends sharded options with high/low-priority pool ratios and adaptive mutex selection. It exposes `MakeSharedCache()` and `MakeSharedRowCache()`, while deprecated `NewLRUCache` overloads wrap those constructors for compatibility. `CompressedSecondaryCacheOptions` extends LRU options with `compression_type`, `compression_opts`, split/merge toggles, and a role set excluded from compression; it returns `std::shared_ptr<SecondaryCache>`.

`HyperClockCacheOptions` configures the recommended high-concurrency block cache. Key fields include `estimated_entry_charge`, `min_avg_entry_charge`, and `eviction_effort_cap`, plus inherited sharding, capacity, allocator, and metadata charge policy. `NewClockCache` is retained only as a compatibility wrapper that returns LRU because the old clock cache was removed. `TieredCacheOptions`, `NewTieredCache`, and `UpdateTieredCache` define an experimental two-tier/three-tier topology across primary uncompressed cache, compressed secondary cache, and optional non-volatile secondary cache.

## Control Flow

Most control flow is construction-time. Callers fill an options struct, then call `MakeSharedCache`, `MakeSharedRowCache`, `MakeSharedSecondaryCache`, `NewTieredCache`, or a deprecated wrapper. The returned shared pointer is installed into DB/table/blob/row-cache options. Runtime update flow exists only for tiered caches: `UpdateTieredCache` mutates total capacity, compressed-secondary ratio, and admission policy for a cache originally built by the tiered factory.

The header's inline wrappers construct temporary option structs and immediately delegate to the method-based factories. That keeps backward-compatible function signatures while centralizing future behavior in options objects.

## State and Persistence Behavior

Cache state is in-memory and non-persistent, but it directly affects persistence-adjacent IO behavior. Block cache contents, blob cache entries, write-buffer charges, and secondary-cache contents influence read amplification, write throttling, and memory pressure, but not the durable key/value state itself. Secondary caches can be non-volatile, and the tiered API can admit compressed blocks to an optional persistent secondary tier; nevertheless this header only models cache configuration, not on-disk format ownership.

The most important mutable state is capacity accounting: charges can include only entry charge or cache metadata overhead, strict capacity can reject insertions under pinned pressure, and WriteBufferManager reservations can be costed into the block cache. Sharding and hash seeds become stable runtime properties that affect contention and eviction distribution.

## Dependencies and Integration Points

The header depends on `compression_type.h`, `data_structure.h`, `memory_allocator.h`, forward-declared `Cache`, `SecondaryCache`, and `ConfigOptions`. It is used by `BlockBasedTableOptions::block_cache`, `DBOptions::row_cache`, blob cache options, WriteBufferManager integration, and tools such as db_bench/db_stress. Search signals show extensive use in table tests, `db_block_cache_test.cc`, `db_write_buffer_manager_test.cc`, `db_stress_test_base.cc`, `tools/db_bench_tool.cc`, Java JNI cache wrappers, and block-based table reader/factory code.

`CacheEntryRole` also integrates with table-builder/reader memory charging, compression dictionary guidance, filter construction, file metadata charging, and the `DB::Properties::kBlockCacheEntryStats` property map.

## Risks and Edge Cases

The aliasing plan for `BlockCache`, `RowCache`, and `Cache` is a compatibility risk: users treating row cache and block cache as fully interchangeable may need migration when the split happens. `CacheEntryRole` has an ordering invariant: adding roles requires updating string tables and keeping `kMisc` last. Misconfigured `num_shard_bits`, tiny shard capacities, or fixed hash seeds can create contention or thrashing. Strict capacity limit can surface insertion failures under pinned entries.

HyperClockCache is not a general cache despite returning `std::shared_ptr<Cache>`; using it outside compatible block-cache paths is risky. `estimated_entry_charge` that is badly wrong can degrade HCC performance. Tiered cache is experimental, has update limitations, and cannot re-enable compressed secondary after disabling it by setting the ratio to zero.

## Test Signals

Relevant tests include `db/db_block_cache_test.cc` for cache role stats and HCC/LRU behavior, `db/db_write_buffer_manager_test.cc` for cache-charged memtable memory, table/block-based tests for block cache interactions, and db_bench/db_stress option paths for realistic cache construction. Role charging validation appears in `table/block_based/block_based_table_factory.cc` and its tests; secondary-cache helpers live under `test_util/secondary_cache_test_util.*`.
