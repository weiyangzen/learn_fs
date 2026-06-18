# sources/storage-engines/tikv/src/storage/mvcc/mvcc_read_tracker.rs

## Purpose

This file implements a process-local MVCC read activity tracker used to identify regions with high redundant MVCC version scans. It aggregates per-region scanned-version counts and request counts above a configurable threshold, then exposes versions-per-second throughput for compaction scoring.

## Important APIs, Types, and Functions

- `MVCC_READ_TRACKER: OnceLock<MvccReadTracker>` is the global tracker slot.
- `init_mvcc_read_tracker` initializes the global tracker with a `GcWorkerConfigManager`; repeated calls are ignored by `OnceLock::set`.
- `RegionMvccReadStats` stores `redundant_versions_scanned` and `total_requests` as `AtomicU64`.
- `RegionMvccReadStats::add_mvcc_versions` increments both counters with relaxed ordering.
- `MvccReadTracker` owns `Arc<DashMap<u64, RegionMvccReadStats>>`, a shared `reset_time_secs`, and the GC worker config tracker.
- `MvccReadTracker::record_read` checks `auto_compaction.mvcc_scan_threshold` dynamically and only records reads whose scanned version count is greater than the threshold.
- `get_mvcc_versions_scanned` returns total scanned versions divided by elapsed seconds since last reset.
- `reset_if_needed` clears all stats and updates the reset time; despite its name, it resets unconditionally.
- `tracked_region_count` and test-only `clear` expose map size and cleanup.

## Control Flow

Readers call `record_read(region_id, mvcc_versions_scanned)`. The tracker reads the current GC worker config, filters below-threshold reads, then inserts or updates a region's stats in the concurrent map. Compaction/scoring code calls `get_mvcc_versions_scanned`, which reads the atomic total for a region, computes elapsed wall-clock seconds from `reset_time_secs`, and returns integer throughput. A periodic compaction runner is expected to call `reset_if_needed` to start a new measurement window.

## State and Persistence Behavior

All state is in memory and shared across tracker clones through `Arc`s. Region counters live in `DashMap`; per-region counters are atomic. There is no persistence across process restarts and no write to the storage engine. Reset clears the whole map, losing all accumulated per-region samples for the previous window.

## Dependencies and Integration Points

The tracker depends on `dashmap` for concurrent per-region storage, `GcWorkerConfigManager` for the dynamic threshold, `OnceLock` for global initialization, and wall-clock `SystemTime`. It integrates with GC/auto-compaction configuration and is intended to feed compaction prioritization with observed MVCC scan pressure.

## Risks and Edge Cases

- `reset_if_needed` does not check time or config; callers must schedule it correctly.
- `SystemTime::duration_since(UNIX_EPOCH).unwrap()` assumes non-pre-epoch system time.
- Reads within the same second as reset return zero throughput because elapsed seconds is zero.
- Relaxed atomics are appropriate for approximate metrics, but not for strict accounting.
- `OnceLock` means tests or subsystems cannot replace the global tracker after first initialization in a process.
- The tracker stores one map entry per region that exceeds threshold during a window; very broad workloads may create many entries until reset.

## Test Signals

Tests cover atomic accumulation, throughput calculation with timing tolerance, non-resetting reads, manual clear, and threshold filtering. Tests build a `GcWorkerConfigManager` through `VersionTrack` and use short sleeps to force nonzero elapsed time.
