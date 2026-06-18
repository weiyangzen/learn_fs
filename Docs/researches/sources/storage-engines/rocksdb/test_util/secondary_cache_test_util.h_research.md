# sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.h

Purpose: declares parameterized cache-test utilities for running the same tests against LRU, fixed HyperClock, and auto HyperClock cache implementations, with optional secondary-cache support.

Important APIs/types: `TestCreateContext` carries a `fail_create_` flag. `WithCacheType::TestItem` is a heap-backed byte buffer with `Buf()`, `Size()`, and `ToString()`. `WithCacheType::NewCache()` builds a cache based on virtual `Type()` and optional `ShardedCacheOptions` modification. Overloads set shard bits, strict capacity, metadata charge policy, or secondary cache. `WithCacheTypeParam` plugs into gtest parameterized tests. `GetTestingCacheTypes()` returns all supported type strings.

State behavior: `estimated_value_size_` influences HyperClock construction. Cache hash seeds are forced to zero for deterministic tests. No persistent state is written.

Dependencies/integration: integrates with `rocksdb/advanced_cache.h` and gtest `WithParamInterface`. Tests inherit this class to obtain cache factories and helpers.

Risks and test signals: unknown type values assert and return null. HyperClock options depend on `estimated_value_size_` and min charge calculations. Tests should exercise each cache type, option modification callback propagation, secondary-cache configuration, and helper retrieval for representative roles.
