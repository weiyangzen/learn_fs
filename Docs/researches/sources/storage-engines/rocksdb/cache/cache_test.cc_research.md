# sources/storage-engines/rocksdb/cache/cache_test.cc

## Purpose
This parameterized GoogleTest suite validates the shared `Cache` interface across RocksDB cache implementations, especially LRU and HyperClock variants supplied by `secondary_cache_test_util::GetTestingCacheTypes()`. It checks usage accounting, pinning, lookup/insert/erase behavior, eviction, capacity, iteration, hash seed behavior, and block-cache uncache aggressiveness logic.

## Important APIs, types, and tests
The test fixture `CacheTest` adapts key encoding: HyperClock requires 16-byte keys while LRU accepts 4-byte keys. It provides helpers for `Lookup`, `Insert`, and `Erase`, a deleter that records deleted integer values, and two caches with different capacities. Basic tests include `UsageTest`, `PinnedUsageTest`, `HitAndMiss`, `InsertSameKey`, `Erase`, `EntriesArePinned`, `EvictionPolicy`, `ExternalRefPinsEntries`, `EvictionPolicyRef`, `EvictEmptyCache`, `EraseFromDeleter`, `ErasedHandleState`, `HeavyEntries`, `NewId`, `ReleaseAndErase`, and `ReleaseWithoutErase`.

Typed-cache tests use a local `Value` class and `BasicTypedSharedCacheInterface`. `SetCapacity` validates LRU capacity changes and cleanup; `SetStrictCapacityLimit` validates strict LRU behavior with and without returned handles; `OverCapacity` checks pinned entries over capacity and different LRU/HyperClock eviction timing. Iteration tests cover `ApplyToAllEntries`, `ApplyToAllEntriesDuringResize`, and `ApplyToHandle`. `DefaultShardBits` checks auto shard-bit selection. `GetChargeAndDeleter` validates charge/helper retrieval. `CacheUniqueSeeds` and `CacheHostSeed` verify quasi-random and host-stable hash seeds and their observable ordering effect. `MiscBlockCacheTest.UncacheAggressivenessAdvisor` checks decision traces for uncache aggressiveness values.

## Control flow, state, and persistence
The tests are in-memory and create fresh caches per fixture or test. They intentionally retain and release `Cache::Handle*` values to test pinning and deletion order. Some tests bypass unsupported behavior for HyperClock, such as guaranteed overwrite on same-key insert and arbitrary capacity adjustment. The test main installs the stack trace handler and runs all tests.

## Dependencies and integration points
The suite integrates `rocksdb/cache.h`, LRU cache construction, typed cache wrappers, block cache helpers, secondary cache test utilities, stack traces, hash containers, string utilities, and GoogleTest. It exercises the public cache contract expected by table readers, block caches, secondary cache wrappers, and memory-accounting users.

## Risks and test signals
Tests encode implementation-specific differences between LRU and HyperClock, so broadening cache implementations requires updating parameter logic or bypasses. Some assertions rely on rough metadata behavior and eviction eventually happening after enough churn. Passing tests signal that core cache semantics, handle lifetimes, accounting, iteration under resize, hash seed options, and uncache advisor thresholds remain compatible across supported cache types.
