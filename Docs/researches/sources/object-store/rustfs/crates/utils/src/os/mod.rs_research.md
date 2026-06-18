# sources/object-store/rustfs/crates/utils/src/os/mod.rs

## Purpose
Provides the cross-platform OS/disk utility facade and shared data structures.

## Important APIs, Types, And Functions
Conditionally declares `fs_type`, `linux`, `unix`, and `windows` modules and re-exports platform-specific `get_info`, `same_disk`, `get_physical_device_ids`, `check_cross_device_mounts`, and `get_drive_stats`; Windows additionally exports `get_volume_serial_number`. `IOStats` models Linux-style block IO counters. `DiskInfo` models capacity, inode counts, filesystem type, device major/minor, name, rotational flag, and request depth.

## Control Flow And State
No runtime state in the facade. Compile-time cfg selects the implementation backend.

## Dependencies And Integration Points
Enabled from `lib.rs` under the `os` feature. Storage initialization, disk validation, monitoring, and platform diagnostics consume the exported functions and shared structs.

## Risks And Test Signals
Semantics differ by platform: Linux has real nested mount and IO stat behavior, while other platforms have no-op/default parts. Tests validate valid/invalid disk info, same-disk behavior, and include an ignored drive-stats default test due to CI instability.
