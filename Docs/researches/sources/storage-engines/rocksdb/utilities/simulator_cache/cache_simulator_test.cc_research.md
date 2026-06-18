# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator_test.cc

Purpose: unit tests for trace-driven cache simulators and hybrid row/block cache behavior.

Important tests: helper methods generate user Get and compaction trace records and assert simulated cache contents. Tests cover `GhostCache` second-hit admission, base `CacheSimulator` user/non-user stats and no-insert compaction behavior, ghost simulator miss behavior, prioritized simulator insertion, hybrid row/block behavior across repeated Gets and different referenced keys, small-cache eviction behavior, no-insert-on-row-miss mode, and ghost-hybrid admission.

Control flow and state: tests use deterministic block keys, referenced row keys, get ids, and small or large LRU capacities. They inspect both simulator counters and underlying simulated cache entries to verify row and block insertions.

Dependencies and integration: uses RocksDB test harness, Env timestamps, trace records, `ExtractUserKey`, and LRU cache options.

Risks and test signals: tests strongly cover simulator policy semantics but do not test `BlockCacheTraceSimulator::InitializeCaches()` invalid-name or warmup reset paths directly. Some miss ratios are compared after integer casts because ratios are floating point percentages.
