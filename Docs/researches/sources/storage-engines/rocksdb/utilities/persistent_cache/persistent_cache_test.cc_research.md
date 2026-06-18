# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.cc

Purpose: implements persistent-cache unit and DB integration tests, plus helper factories for volatile, block, and tiered cache configurations.

Important APIs/tests: helpers `NewTieredCache`, `NewBlockCache`, `MakeVolatileCache`, `MakeBlockCache`, and `MakeTieredCache` create concrete tiers. `FactoryTest` actively validates `NewPersistentCache()` for NVM and non-NVM options and checks stats availability. `PersistentCacheDBTest.BasicTest` actively runs a DB/table integration using block persistent cache. Many direct tier stress tests for insertion, eviction, tiering, and file-create error are disabled due to cost/environment constraints.

Control flow and state: Linux sync points disable `O_DIRECT` and mock unique-id behavior for test environments. DB tests create a column family with block-based table persistent cache, write compressible data, flush to SST, read twice, and assert persistent-cache hit/miss tickers were exercised.

Dependencies and integration: uses `DBTestBase`, block-based table options, transaction-free DB reads/writes, `SyncPoint`, file utilities, and `BlockCacheTier`.

Risks and test signals: active tests validate integration more than exhaustive eviction/file-IO behavior. Disabled tests are still valuable as design intent for stress, direct writes, volatile eviction, block eviction, and tiered cache behavior. Sync-point callbacks are platform-sensitive and Linux-specific.
