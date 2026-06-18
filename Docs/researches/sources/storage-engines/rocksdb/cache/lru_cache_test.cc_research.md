# sources/storage-engines/rocksdb/cache/lru_cache_test.cc

## Purpose
This GoogleTest file validates LRU cache behavior, clock-cache behavior colocated in the same test file, secondary-cache integration, DB/block-cache integration, cache dump/load into secondary cache, and DB options that enable or bypass secondary cache tiers.

## Important APIs, Types, And Functions
`LRUCacheTest` manually constructs one `LRUCacheShard` and provides helpers for insert, lookup, erase, and exact LRU-list validation. Its tests cover basic LRU order, low-priority midpoint insertion, bottom-priority behavior, priority-pool overflow, and insertion after capacity reduction. The `clock_cache` namespace defines templated `ClockCacheTest` tests for `AutoHyperClockCache` and `FixedHyperClockCache`, including limits, eviction, counter overflow, collisions, and table sizing. `TestSecondaryCache` is a fake `SecondaryCache` backed by an LRU typed cache and supports success, immediate failure, deferred success, and deferred failure. `BasicSecondaryCacheTest` and `DBSecondaryCacheTest` use `NewCache()` with a secondary cache to validate primary/secondary behavior in direct cache and real DB paths. `CacheWithStats` wraps a cache to count inserts and lookups for dump/load tests.

## Control Flow
The LRU unit tests construct a shard, insert keys with different priorities, perform lookups that temporarily pin entries and then release them, and assert precise LRU-list partitioning after each transition. Secondary-cache tests force primary-cache eviction by using small capacities, then verify lookup promotion from `TestSecondaryCache` and demotion on later evictions. DB tests create SST files with known block sizes so data-block cache misses, promotions, and evictions can be observed through secondary-cache insert/lookup counters. Dump/load tests populate a block cache, dump entries through `CacheDumper`, restore them into a secondary cache, reopen a DB, and confirm reads are served through secondary-cache lookups.

## State And Persistence Behavior
Most tests use in-memory cache state, but DB tests create actual RocksDB test databases and SST files. `TestSecondaryCache` serializes values by prefixing a size and storing bytes in an internal LRU cache. It tracks `num_inserts_`, `num_lookups_`, failure injection, saved insertion behavior, a common cache-key prefix, and per-key result modes. The dump/load tests persist cache dumps to files under the test DB path and reload them into secondary cache, validating cache-warm persistence behavior rather than database correctness alone.

## Dependencies And Integration Points
The file depends on LRU and clock cache internals, `cache_helpers.h`, typed cache helpers, DB test utilities, block-based table options, cache dump/load utilities, fault-injection file systems, sync points, and secondary-cache test utilities. It integrates cache APIs with RocksDB block cache, paranoid file checks, compaction, `MultiGet`, `lowest_used_cache_tier`, and unique cache keys.

## Risks And Edge Cases
The tests document several tricky behaviors: LRU-specific over-capacity release behavior differs from HyperClock, secondary-cache insertion errors are intentionally ignored on demotion, promotion can return standalone handles if primary insertion fails, disabled secondary cache must not perform lookup or insertion, shared caches across DBs must respect per-DB cache-tier options, and async `WaitAll()` must process deferred successes and failures without corrupting results. Exact block-count assertions can be sensitive to table-format changes, metadata accounting, or cache-key generation.

## Test Signals
The file is a major behavioral test signal. It asserts exact list order/pool counts, exact secondary insert/lookup counts, per-role secondary hit tickers, `PerfContext::secondary_cache_hit_count`, DB read correctness after cache misses/promotions, no-I/O validation after dump/load with a fault-injection file system, and async lookup results after `WaitAll()`.
