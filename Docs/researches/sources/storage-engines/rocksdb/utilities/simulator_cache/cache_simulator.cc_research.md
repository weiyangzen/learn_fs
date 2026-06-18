# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.cc

Purpose: implements trace-driven block-cache simulators that replay `BlockCacheTraceRecord` events against simulated LRU caches and report miss-ratio statistics for different policies.

Important APIs and control flow: `GhostCache::Admit()` implements second-hit admission. `CacheSimulator::Access()` performs ordinary block lookup/insert and updates metrics. `MissRatioStats::UpdateMetrics()` aggregates total/user accesses, misses, and per-second timelines. `PrioritizedCacheSimulator` assigns high priority to filter/index/uncompression-dictionary blocks and centralizes `AccessKVPair()`. `HybridRowBlockCacheSimulator` models row-key-value caching for Get requests, using `get_id` state to skip later block accesses after a row hit. `BlockCacheTraceSimulator::InitializeCaches()` builds configured simulator instances, including ghost variants, and `Access()` handles warmup reset and fanout.

State and persistence: simulation state lives in RocksDB `Cache` instances, optional ghost caches, miss-ratio counters, per-Get row status maps, and simulator configuration maps. No persistent output is written here; consumers read stats from objects.

Dependencies and integration: uses LRU cache factory, block cache tracer records/helpers, trace enums, RocksDB cache priority, and `ExtractUserKey` through trace helpers. It supports policies named `lru`, `lru_priority`, `lru_hybrid`, and `lru_hybrid_no_insert_on_row_miss`, optionally prefixed with `ghost_`.

Risks and test signals: timestamp variable names mix milliseconds/microseconds, but code divides microsecond trace timestamps by `kMicrosInSecond`. `downsample_ratio_` is used as a divisor without explicit zero validation. Hybrid state can grow by `get_id` count. Tests cover ghost admission, basic/prioritized/hybrid policies, no-insert behavior, row-key insertion, and ghost-hybrid behavior.
