# sources/storage-engines/rocksdb/cache/tiered_secondary_cache_test.cc

## Purpose
Exercises tiered cache behavior through DB-level reads, MultiGet, iteration, admission policies, and filesystem buffer ownership. It uses a fake NVM `SecondaryCache` to count inserts, hits, and misses while validating interactions between primary cache, compressed secondary cache, and an NVM secondary tier.

## Important APIs and Test Fixtures
`TestSecondaryCache` stores serialized saved blocks in an LRU cache using `BasicTypedSharedCacheInterface<char[]>`; saved entries include payload size, compression type, cache tier, and bytes. Its `Lookup` decodes the saved record and invokes the caller's `create_cb`, returning a `TestSecondaryCacheResultHandle` that can be ready immediately or after `WaitAll`. `DBTieredSecondaryCacheTest::NewCache` builds a tiered cache with primary/compressed/NVM capacities and exposes helper accessors for NVM counters and compressed secondary usage.

## Control Flow and State
`BasicTest` validates warming NVM on SST misses, NVM hits, placeholder promotion, primary hits, and later compressed-secondary hits. `BasicMultiGetTest`, `WaitAllTest`, and `ReadyBeforeWaitAllTest` cover async lookup, wait aggregation, readiness before wait, and block-cache miss tickers. `IterateTest` validates readahead iteration warms and reuses NVM blocks. `VolatileTierTest` verifies `lowest_used_cache_tier == kVolatileTier` bypasses secondary cache. Parameterized tests compare admission policies for compressed-only cache. `FSBufferTest` wraps `MultiRead` to exercise `FSAllocationPtr` scratch ownership. Risks are timing-sensitive async assumptions and small cache-capacity math; tests skip when LZ4 is unavailable.
