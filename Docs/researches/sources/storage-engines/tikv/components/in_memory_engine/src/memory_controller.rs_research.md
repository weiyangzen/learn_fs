# sources/storage-engines/tikv/components/in_memory_engine/src/memory_controller.rs

## Purpose

Tracks and limits in-memory engine memory usage using exact allocated key/value byte counts plus estimated skiplist node overhead, and exposes threshold checks used by writes, loads, and eviction scheduling.

## Important APIs, Types, And Functions

`MemoryUsage` reports `NormalUsage(usize)`, `EvictThresholdReached(usize)`, or `CapacityReached(usize)`. `MemoryController` stores an atomic `allocated` byte count, shared `VersionTrack<InMemoryEngineConfig>`, a `memory_checking` flag, and the `SkiplistEngine` used for node-count overhead. `new` constructs the controller. `acquire` attempts to reserve bytes and returns a threshold/capacity result, rolling back the reservation when capacity would be exceeded. `release` subtracts bytes. `reached_stop_load_threshold`, `stop_load_threshold`, `evict_threshold`, `set_memory_checking`, `memory_checking`, and `mem_usage` expose threshold and current-usage state.

## Control Flow

Writers/loaders call `acquire(n)` before inserting key/value wrappers into the skiplist. The method adds `n`, computes total memory as allocated bytes plus `skiplist_engine.node_count() * NODE_OVERHEAD_SIZE_EXPECTATION`, and compares it to live config thresholds. If the capacity would be reached, it subtracts `n` and returns `CapacityReached(previous_usage)`. If only the eviction threshold is reached, it keeps the reservation and returns `EvictThresholdReached`. Inserted `InternalBytes` later call `release` on drop, returning their accounted size.

## State And Persistence Behavior

All state is volatile and process-local. `allocated` intentionally excludes skiplist node overhead, which is recomputed from current node count. Because config is read from `VersionTrack` on each call, online capacity/threshold changes take effect without rebuilding the controller.

## Dependencies And Integration Points

Depends on `InMemoryEngineConfig`, `SkiplistEngine`, and `write_batch::NODE_OVERHEAD_SIZE_EXPECTATION`. It is created by `RegionCacheMemoryEngine`, passed into `BgWorkManager`, used by write batches and background loading/filtering, and embedded indirectly in `InternalBytes` for release-on-drop.

## Risks

Memory accounting is approximate and relaxed-atomic; it is designed for threshold control rather than byte-perfect enforcement. Concurrent `acquire` calls can temporarily observe stale node counts or threshold values. A bad `release` call with an incorrect size would underflow the atomic counter. The capacity check uses `>=`, so equal-to-capacity acquisitions are rejected and return the usage before the attempted allocation.

## Test Signals

`test_memory_controller` verifies normal, eviction-threshold, and capacity results; rollback of failed capacity acquisition; release behavior; node-overhead contribution after a skiplist insert; and threshold behavior after a node is removed.
