# sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.cc

Purpose: implements cache item helpers used by secondary-cache tests, including serialization, creation, size accounting, and failure injection.

Important APIs/functions: `WithCacheType::GetHelper()` returns a static `Cache::CacheItemHelper` for a cache-entry role with optional secondary-cache compatibility and optional save failure. `GetHelperFail()` is a convenience for failing save-to-secondary paths. Internal callbacks delete `TestItem`, compute size, serialize the entire buffer from offset zero, fail serialization, or reconstruct a `TestItem` from secondary-cache bytes.

State and ownership: helper arrays are static and indexed by `CacheEntryRole`. `CreateCallback()` allocates `TestItem` with `new`; `DeletionCallback()` owns deletion. `TestCreateContext::fail_create_` can force creation failure.

Dependencies/integration: uses advanced cache APIs and gtest expectations. It supports LRU and HyperClock cache test coverage through the declarations in the header.

Risks and test signals: `SaveToCallback()` expects full-object serialization from offset zero, so tests using partial offsets will fail. Role indexing assumes `kNumCacheEntryRoles` matches enum ordinals. Tests should cover all roles, successful secondary round trip, save failure, create failure, and helper chaining through the `without_secondary` fallback pointer.
