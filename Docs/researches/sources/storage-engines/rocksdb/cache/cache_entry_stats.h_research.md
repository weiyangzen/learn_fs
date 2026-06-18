# sources/storage-engines/rocksdb/cache/cache_entry_stats.h

## Purpose
This templated header provides `CacheEntryStatsCollector<Stats>`, a reusable mechanism for collecting expensive cache-entry statistics through `Cache::ApplyToAllEntries()` while sharing and caching recent results per `Cache` instance.

## Important APIs, types, and functions
The `Stats` template contract requires `BeginCollection(Cache*, SystemClock*, uint64_t)`, `GetEntryCallback()`, `EndCollection(Cache*, SystemClock*, uint64_t)`, and `SkippedCollection()`, plus copyability and trivial construction. `CollectStats(min_interval_seconds, min_interval_factor)` serializes collectors with `working_mutex_`, computes a maximum acceptable cached-result age from an absolute interval and a multiple of the previous collection duration, scans the cache when stale, or calls `SkippedCollection()` when recent enough. It copies working stats into `saved_stats_` under `saved_mutex_`. `GetStats()` returns the saved copy. `GetShared()` stores a single collector object inside the cache using `BasicTypedCacheInterface<CacheEntryStatsCollector, CacheEntryRole::kMisc>` and a process-lifetime `CacheKey`, with a static mutex to avoid duplicate insert races, then returns an aliasing `shared_ptr` via `SharedGuard()`.

## Control flow, state, and persistence
State is in-memory and per cache: saved stats, working stats, last start/end timestamps, the raw cache pointer, and a clock pointer. The collector object is itself held as a cache entry with zero charge, so its lifetime is tied to cache handles/shared guards. The initial `last_end_time_micros_` value is pessimistic, helping first-collection age logic.

## Dependencies and integration points
The collector integrates with typed cache wrappers, `CacheKey::CreateUniqueForProcessLifetime()`, system clocks, `ApplyToAllEntries`, and test sync points. It supports block cache property collectors that would otherwise each rescan the whole cache for every DB or column family sharing a cache.

## Risks and test signals
The raw `Cache*` and `SystemClock*` must outlive collector use. Zero charge avoids flaky cache-usage tests but means metadata accounting understates the collector. `GetShared()` still has a lookup/insert race without the static mutex; that mutex is global per template instantiation. Test by concurrent callers sharing one cache, repeated stats calls within and beyond the min interval, and cache destruction with outstanding shared guards.
