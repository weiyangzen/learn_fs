# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_drive.rs

## Purpose
Defines detailed system drive descriptors for capacity, capacity-observation state, inode counts, errors, queueing/latency, health, aggregate online/offline counts, and iostat-like rates.

## Important APIs, Types, and Functions
Exports label constants `DRIVE_LABEL`, `SERVER_LABEL`, `POOL_INDEX_LABEL`, `SET_INDEX_LABEL`, `DRIVE_INDEX_LABEL`, and `API_LABEL`. `ALL_DRIVE_LABELS` includes drive/pool/set/drive-index. Capacity, inode, waiting IO, latency, health, count, and iostat values are gauges; timeout, I/O, and availability errors are counters. Capacity observation state adds a `state` label, and API latency adds an `api` label.

## Control Flow
Descriptors are lazily initialized. Some label slices are built by concatenating arrays at initialization time.

## State and Persistence
No values here. `collect_disk_and_system_drive_stats()` reads storage admin `storage_info`, computes online/offline counts, capacity observation states (`live`, `stale`, `missing`), and derives utilization percentage from used/total bytes. Many iostat/error/inode fields currently default to zero.

## Dependencies and Integration Points
Used by `metrics/collectors/system_drive.rs`, which must attach all drive labels and any extra `state` or `api` labels. Integrates with storage topology fields such as pool/set/drive indexes through collector/stat DTOs.

## Risks
There is a potential label contract mismatch to watch: `ALL_DRIVE_LABELS` omits `server`, while collector helpers may provide server/drive labels. If descriptor labels and collector labels diverge, Prometheus output can be inconsistent. Many fields are placeholders until storage/iostat sources are wired. The help text contains a micro sign in one string; encoding should remain UTF-8.

## Test Signals
Collector tests check representative drive names and counts. `stats_collector.rs` tests cover online/offline state interpretation and capacity observation state indirectly through count behavior.
