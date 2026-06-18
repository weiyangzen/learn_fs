# sources/storage-engines/tikv/components/in_memory_engine/src/region_stats.rs

## Purpose

This file implements the policy layer for automatic region loading and eviction based on raftstore region activity, memory-controller thresholds, and smoothed coprocessor request rates. It chooses top regions to load and low-value cached regions to evict.

## Important APIs, Types, And Functions

- `RegionStatsManager` holds config, a `RegionInfoProvider`, a concurrency flag, region load timestamps, eviction minimum duration, and last check time.
- `ready_for_auto_load_and_evict` and `complete_auto_load_and_evict` throttle and serialize policy runs.
- `collect_regions_to_load_and_evict` returns regions to load and regions to evict based on top-region stats, cached-region stats, and memory pressure.
- `evict_on_evict_threshold_reached` evicts low-read-flow regions in small batches when memory has crossed the eviction/stop-load threshold.
- `CachedRegionStat` stores region, raw stat, SMA count/average, and iterated count.
- `sort_cached_region_stats` updates each cached region's SMA and sorts by low coprocessor requests, then low iterated count.

## Control Flow

Policy checks are allowed only after a minimum interval and when no check is already running. `collect_regions_to_load_and_evict` first queries stats for cached regions, estimates how many regions can fit before the evict threshold using expected region size, then asks raftstore for that many top regions. Top regions not already cached become load candidates and are recorded with load timestamps. Cached regions are sorted by low activity. If cached count is too small, no eviction occurs. Under stop-load memory pressure, the policy computes average iterated count and SMA coprocessor requests, then selects at most one tenth of cached regions whose request average and iterated count are much lower than average, whose SMA has enough samples, and whose load timestamp exceeds `evict_min_duration`.

`evict_on_evict_threshold_reached` separately handles direct memory pressure: it filters cached regions to those at or below average SMA request rate, evicts chunks of two via a supplied callback, schedules background delete-range work, waits for eviction-finished callbacks to signal memory release, and stops once memory is below the stop-load threshold.

## State And Persistence Behavior

The manager persists no data. It keeps in-memory timing and SMA state through shared `CopRequestsSma` instances owned by region metadata. Region load timestamps are updated as top regions are observed and cleared when a region is evicted.

## Dependencies And Integration Points

The file depends on `raftstore::coprocessor::RegionInfoProvider`, `pd_client::RegionStat`, `MemoryController`, `VersionTrack<InMemoryEngineConfig>`, `BackgroundTask` scheduling, `engine_traits::{CacheRegion, EvictReason, OnEvictFinishedCallback}`, and metrics histograms for auto load/evict observations. It consumes cached-region SMA handles from `RegionMetaMap::cached_regions` and calls `RegionManager` eviction through injected closures.

## Risks And Edge Cases

The policy is heuristic and workload-sensitive. It assumes post-cache request patterns remain representative and deliberately avoids using low MVCC amplification alone as an eviction reason for cached regions. Region stat provider failures log and assert shutdown in non-test mode, returning no changes. Timestamps for newly observed top regions can delay eviction even if a region becomes idle quickly. Waiting for eviction callbacks avoids tight loops but can stall if callbacks are not invoked.

## Test Signals

Tests use a `RegionInfoSimulator` to validate top-region loading, SMA warm-up, idle-region eviction after sufficient samples and duration, no eviction below memory pressure, eviction callback batching/order under threshold pressure, check throttling, and cached-region sort order.
