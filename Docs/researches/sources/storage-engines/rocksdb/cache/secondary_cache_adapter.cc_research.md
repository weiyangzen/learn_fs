# sources/storage-engines/rocksdb/cache/secondary_cache_adapter.cc

## Purpose
This file implements `CacheWithSecondaryAdapter`, the wrapper that combines a primary RocksDB `Cache` with a `SecondaryCache`, plus factory/update helpers for tiered primary plus compressed-secondary caches. It is the main integration point for eviction demotion, secondary lookup promotion, async lookup chaining, admission policy, and distributed reservation accounting.

## Important APIs, Types, And Functions
The constructor installs a primary-cache eviction callback and optionally initializes reservation accounting for tiered compressed-secondary caches. `EvictionHandler()` spills compatible evicted objects to the secondary cache according to `TieredAdmissionPolicy`. `Insert()` forwards to the target cache, handles placeholder reservation redistribution, and warms the secondary cache with compressed saved values for three-queue policy. `Lookup()` checks the primary cache, processes dummy entries, then synchronously queries the secondary cache and calls `Promote()`. `Promote()` records secondary-hit stats and inserts the result into primary cache or returns a standalone handle with a dummy marker. `StartAsyncLookup()`, `StartAsyncLookupOnMySecondary()`, and `WaitAll()` chain asynchronous lookups through inner and outer secondary caches. `SetCapacity()`, `GetSecondaryCacheCapacity()`, `GetSecondaryCachePinnedUsage()`, `UpdateCacheReservationRatio()`, and `UpdateAdmissionPolicy()` manage dynamic tiered-cache settings. `NewTieredCache()` and `UpdateTieredCache()` are public factory/update helpers.

## Control Flow
On eviction, the primary cache calls `EvictionHandler()`, which checks helper compatibility and admission policy before calling `secondary_cache_->Insert()`. On lookup, the adapter first delegates to the primary cache; if it finds a dummy entry, it releases and optionally erases it. A secondary hit is promoted: if the secondary supports force erase and no dummy marker was found, the adapter returns a standalone handle and inserts a dummy marker; otherwise it tries a normal primary insert and falls back to standalone if primary insertion fails. Async lookup first starts through the target cache and only starts the adapter's own secondary lookup when no inner pending lookup or result exists; `WaitAll()` waits inner caches first, then starts/waits the outer secondary tier for remaining misses.

## State And Persistence Behavior
Persistent state is external to this file; adapter state is in-memory wrapper state. It owns `secondary_cache_`, current admission policy, whether cache reservations are distributed, a primary `ConcurrentCacheReservationManager`, `sec_cache_res_ratio_`, and counters for placeholder usage, reserved usage, and secondary-reserved bytes. Reservation changes happen in 1 MiB chunks. `kDummyObj` is a sentinel object used to record recent secondary access without holding the full object in primary cache.

## Dependencies And Integration Points
The implementation depends on `cache/tiered_secondary_cache.h`, stats/perf counters, sync points, cast utilities, `LRUCacheOptions`, `HyperClockCacheOptions`, `NewCompressedSecondaryCache()`, and public `Cache`/`SecondaryCache` helper contracts. It is invoked from `LRUCacheOptions::MakeSharedCache()` when `secondary_cache` is set and from `NewTieredCache()` for combined primary/compressed/nvm tiering.

## Risks And Edge Cases
Ownership and lifetime are subtle: the destructor must clear the target eviction callback to avoid use-after-free; `Promote()` must not double-free objects when primary insertion fails or when a secondary cache keeps its copy; dummy entries must never be exposed through `Value()`. Reservation redistribution relies on assertions that secondary `Deflate()`, `Inflate()`, and reservation updates succeed. Stacked secondary caches have a documented false synchronization point in `WaitAll()`. Admission policy validation must reject incompatible NVM/compressed combinations.

## Test Signals
`lru_cache_test.cc` validates synchronous and async promotion, stats by cache-entry role, failure modes, full-capacity standalone promotion, DB integration, `MultiGet`, dump/load, and per-DB tier disabling. `compressed_secondary_cache_test.cc` validates compressed/tiered reservation distribution, admission policies, dynamic capacity/ratio updates, and `NewTieredCache()` behavior.
