# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_bench.cc

Purpose: gflags benchmark driver for persistent-cache tiers: disk block cache, volatile RAM cache, and tiered volatile+block cache.

Important APIs/types: factory helpers build `VolatileCacheTier`, `BlockCacheTier`, or `PersistentTieredCache` from flags. `CacheTierBenchmark` optionally prepopulates one million keys, starts write/read threads, runs for `FLAGS_nsec`, prints local latency/byte histograms and cache stats, flushes, and closes the cache.

Control flow and state: keys are fixed 24-byte binary slices from three `uint64_t`s, values are deterministic byte patterns of `FLAGS_iosize`. Writers insert monotonically increasing keys; readers pick random keys below `read_key_limit_`. `Prepop()` also warms reads before timed stats.

Dependencies and integration: requires gflags, uses RocksDB histograms, system clock, Env logging, block builder include, and persistent-cache tier implementations. It is operational tooling for tuning `writer_iosize`, queue depth, pipelining, cache size, and tier mix.

Risks and test signals: with `GFLAGS` absent the file builds a stub main. It asserts on lookup status unless benchmark mode only relaxes content verification. `NewVolatileCache()` passes `FLAGS_cache_size` to the first constructor argument of `VolatileCacheTier`, which is `is_compressed`, not `max_size`, so this helper appears suspect in this snapshot. Bench results are not correctness tests.
