# sources/storage-engines/tikv/components/engine_traits/src/region_cache_engine.rs

Purpose: Defines an optional region cache engine abstraction for in-memory or NVMe accelerated reads.

Important APIs and control flow: `FailedReason` explains cache snapshot failures. `RegionEvent` models split, try-load, eviction, and range eviction, with debug output hiding callback internals. `EvictReason` enumerates eviction causes. `RegionCacheEngine` creates cache snapshots for a `CacheRegion`, read timestamp, and shared sequence number, connects a disk engine, starts a hint service, and reports enablement. `RegionCacheEngineExt` handles events, cache presence, and loads. `CacheRegion` wraps encoded region bounds and provides contains, overlaps, union, and difference operations.

State, persistence, and dependencies: Cache engines own non-authoritative cached region state synchronized with disk engine sequence numbers. Dependencies include region metadata and encoded TiKV keys.

Integration points, risks, and test signals: Integrated with raftstore region events, read paths, delete-range eviction, and range hints. Risks include epoch races, boundary encoding mistakes, stale cache after split/merge/snapshot, callback lifecycle, and disabled default behavior. Unit tests cover overlap semantics; integration tests must cover cache invalidation and snapshot fallback.
