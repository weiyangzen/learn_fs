<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs

### Purpose
Defines cache configuration, adaptive TTL calculation, cache statistics, and cache health classification for object caching.

### Important APIs, Types, And Functions
`CacheConfig` contains capacity, TTL range, memory limit, shard count, adaptive TTL flag, and hot/cold TTL factors. It supports `validate`, duration accessors, and builder methods. `CacheConfigError` reports invalid values. `AdaptiveTTL` stores config, hot/cold thresholds, and access window, with `calculate_ttl`, `should_evict_early`, and `calculate_priority`. `CacheStats` tracks hits, misses, entries, memory, evictions, TTL expirations, and hit/miss rates. `CacheHealthStatus` maps hit rate to healthy/degraded/unhealthy/unknown.

### Control Flow
Validation rejects zero capacity, invalid TTL ordering, default TTL outside range, and invalid extension/reduction factors. TTL calculation optionally extends hot items, reduces cold items, applies hit-rate-based adjustment, and clamps to configured min/max. Early eviction returns true for cold items older than half their current TTL. Priority combines access frequency, recency, and inverse size.

### State And Persistence
All structs are in-memory value types. `CacheStats` is mutable but not atomic; synchronization is caller-owned.

### Dependencies And Integration Points
Uses `num_cpus::get()` for default shard count and `Duration` for TTL. Re-exported from `lib.rs` and demonstrated in the example. Works with `adaptive_ttl::AccessTracker` and cache metrics helpers.

### Risks
`CacheHealthStatus::from_hit_rate` treats any non-negative value below 0.5 as unhealthy and only negative as unknown; values greater than 1.0 become healthy. `should_evict_early` ignores recency beyond age and access count. Priority can heavily penalize large objects, which may be intended but can evict valuable large hot data. Config validation does not check max memory or shard count.

### Test Signals
Tests cover defaults, validation failures, hot/cold TTL adjustment, cache stat rates, health mapping, early eviction, and priority ordering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs -->
