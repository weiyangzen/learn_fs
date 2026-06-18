# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.h

Purpose: declares cache simulator configurations, miss-ratio statistics, admission policy helpers, and simulator classes for block-cache trace replay.

Important APIs/types: `CacheConfiguration` identifies cache name, shard bits, ghost capacity, and capacity sweep values, with comparison operators for map keys. `MissRatioStats` exposes reset, total/user miss ratios, counters, timelines, and `UpdateMetrics`. `GhostCache` controls second-access admission. `CacheSimulator`, `PrioritizedCacheSimulator`, `HybridRowBlockCacheSimulator`, and `BlockCacheTraceSimulator` form the simulator hierarchy.

Control flow and state: base simulator tracks one simulated cache plus optional ghost cache. Prioritized simulator adds priority classification and shared lookup/insert helper. Hybrid simulator tracks per-Get completion and row-key insertion state. Trace simulator owns a map from configuration to capacity-specific simulator objects and manages warmup.

Dependencies and integration: includes LRU cache and block-cache tracer headers. It is used by simulator tests and by tooling that consumes RocksDB block-cache traces.

Risks and test signals: `CacheConfiguration::operator==` ignores `cache_capacities`, while `operator<` also ignores it; this groups all capacities under one configuration key by design because values live in the mapped vector. Callers must avoid zero downsample ratios. Unit tests exercise most declared simulator classes.
