# sources/storage-engines/tikv/components/tikv_util/src/sys/disk.rs

## Purpose
Maintains process-wide disk capacity/usage/reservation/status snapshots and exposes filesystem free-space stats.

## Important APIs, Types, and Functions
- Atomic setters/getters for disk capacity, used size, available size, reserved space, and raft reserved space.
- `set_disk_status` and `get_disk_status(store_id)` encode/decode `kvproto::disk_usage::DiskUsage`.
- `get_disk_space_stats(path)` returns total and available space via `fs2::statvfs`.

## Control Flow
Setters store values with release ordering; getters load with acquire ordering. `get_disk_status` first checks per-store failpoints for almost-full/already-full overrides, then maps the stored integer to the protobuf enum. Disk-space stats can be replaced by a failpoint-provided `capacity,available` pair.

## State and Persistence Behavior
All disk state is in static atomics for process lifetime. It represents the latest values set by monitors and is not persisted.

## Dependencies and Integration Points
Depends on `kvproto::disk_usage::DiskUsage`, `fail`, `fs2`, and `Path`. Store/raft monitoring code can set these values, while scheduling or health checks can read them.

## Risks
The status integer panics if corrupted to an unexpected value. Values are global, while failpoints allow store-specific status injection for stores 1 through 5. Stale values remain until updated by external monitor code.

## Test Signals
`sys/mod.rs` tests cover `get_disk_space_stats` for the current directory and an invalid path. Failpoints provide additional test hooks.
