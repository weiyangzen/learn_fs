# sources/object-store/rustfs/crates/utils/src/os/unix.rs

## Purpose
Implements non-Linux Unix disk utilities using POSIX `statvfs`/`stat`, with simplified physical-device and mount checks.

## Important APIs, Types, And Functions
`get_info` uses `rustix::fs::statvfs` to compute total/free/used bytes from fragment size, available blocks, and reserved blocks, then uses `stat` for major/minor. `same_disk` compares `st_dev`. `get_physical_device_ids` returns a single `major:minor` string. `check_cross_device_mounts` is a no-op. `get_drive_stats` returns default `IOStats` on non-Linux.

## Control Flow And State
Stateless. `get_info` validates `bavail <= bfree`, reserved blocks not exceeding total blocks, and free not exceeding total before returning `DiskInfo`.

## Dependencies And Integration Points
Compiled for Unix targets other than Linux. Uses `rustix::fs::{statvfs, stat}` and shared `DiskInfo`/`IOStats` from `os/mod.rs`.

## Risks And Test Signals
Filesystem type is always `UNKNOWN`, nested mount validation is absent, and physical identity is less precise than Linux leaf-device traversal. Shared facade tests exercise basic `get_info` and `same_disk` behavior; platform-specific edge coverage is limited.
