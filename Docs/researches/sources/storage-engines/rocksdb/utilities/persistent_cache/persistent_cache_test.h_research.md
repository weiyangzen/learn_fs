# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.h

Purpose: declares test fixtures and reusable workloads for persistent-cache tier and DB tests.

Important APIs/types: `PersistentCacheTierTest` provides `Flush`, thread spawn/join helpers, threaded `Insert` and `Verify`, padded key generation, and test templates for normal, negative, and eviction-enabled insert runs. `PersistentCacheDBTest` extends `DBTestBase` and provides ticker access, `Insert`, `Verify`, and `RunTest`.

Control flow and state: tier tests generate `key_prefix_` keys and 4KB deterministic values, retry `TryAgain` inserts, flush queued writes, then verify hits/misses across threads. DB tests write into a secondary column family named `pikachu`, disable block cache for default CF, flush to SST, and read values twice to exercise cache behavior.

Dependencies and integration: includes RocksDB DB test utilities, block builder/table options, test harness, random, and volatile cache. It is included by `persistent_cache_test.cc`.

Risks and test signals: workload helpers assume absent lookup during eviction means acceptable eviction, while non-eviction paths require every key to be present. The destructor closes any remaining cache, so tests that already close reset `cache_` to avoid double use. Most direct tier tests using this fixture are disabled in the implementation file.
