# sources/storage-engines/tikv/components/in_memory_engine/src/region_manager.rs

## Purpose

This file owns cached-region metadata, the region cache state machine, active snapshot tracking, split/epoch handling, manual load ranges, and eviction eligibility. It is the coordination layer that keeps foreground reads, raftstore region events, GC, writes, and background delete-range tasks consistent.

## Important APIs, Types, And Functions

- `RegionState` models `Pending`, `Loading`, `Active`, `LoadingCanceled`, `PendingEvict`, and `Evicting`, with validated state transitions.
- `SnapshotList` tracks active snapshot read timestamps and reference counts.
- `CacheRegionMeta` stores a `CacheRegion`, safe point, state, snapshot list, GC/write flags, eviction info/callback, and smoothed coprocessor request state.
- `RegionMetaMap` indexes active metadata by range end key and region id, detects overlaps, manages manual load ranges, and admits new loads.
- `RegionManager` wraps `RegionMetaMap`, historical split regions with live snapshots, a single-GC-task flag, and an active fast-path flag.
- `LoadFailedReason` distinguishes overlap, pending range, and evicting conflicts, including whether the same region caused the failure.
- `RegionCacheStatus` summarizes public cache status values.

## Control Flow

Loads enter `RegionMetaMap::load_region`, which rejects overlaps or same-id conflicts unless stale pending metadata can be removed. Snapshots call `region_snapshot`, requiring an active matching-epoch region and `read_ts > safe_point`, then increment the snapshot list. Dropping a snapshot calls `remove_region_snapshot`, which decrements either current metadata or historical split metadata and returns regions whose pending eviction is no longer blocked.

Eviction starts with `evict_region`, resolving the exact region or all overlapped regions. Pending regions are removed immediately; active regions become `PendingEvict`; loading regions become `LoadingCanceled`; already-evicting states are ignored. If no current or historical snapshots overlap, `PendingEvict` advances to `Evicting` and the caller receives ranges that can be physically deleted. `on_delete_regions` removes metadata, observes eviction duration, and runs completion callbacks. Splits remove the source region, derive child metadata preserving safe point/state/flags, and move the source to `historical_regions` if old snapshots still exist.

## State And Persistence Behavior

All metadata is memory-resident. The authoritative persisted data remains in RocksDB and the skiplist cache contents are cleaned asynchronously by background delete-range tasks. `historical_regions` is a temporary in-memory structure that prevents deletion of split descendants while pre-split snapshots remain alive. `is_active` is an atomic fast-path signal for whether any region metadata exists.

## Dependencies And Integration Points

The manager depends on `engine_traits::{CacheRegion, EvictReason, FailedReason, OnEvictFinishedCallback}`, `parking_lot::RwLock`, standard mutex/atomics, `tikv_util::smoother::Smoother`, local metrics, and `read::RegionCacheSnapshotMeta`. It is called by snapshot creation/drop in `read.rs`, raftstore/apply event handling in the engine, GC/write paths, memory-pressure eviction, region stats policy, and background deletion completion.

## Risks And Edge Cases

Correctness relies on strict state-transition assertions and non-overlapping range invariants. Stale pending epochs can be replaced only when containment rules hold; same-id non-overlapping conflicts are rejected for implementation simplicity. Active snapshots and historical regions can delay physical eviction and memory release. `on_delete_regions` unwraps eviction info and asserts epoch matches, so callers must only pass regions that reached `Evicting`. Manual load ranges are stored as a vector with union/difference logic that must preserve non-overlap expectations without sorting guarantees.

## Test Signals

Tests cover snapshot safe-point checks, split with historical snapshots, eviction readiness, load conflict reasons, same-id overlap behavior, multi-region eviction, and manual load range overlap/add/remove cases. The `Drop` check on `RegionMetaMap` verifies range and id indexes remain consistent in tests.
