# sources/object-store/rustfs/crates/utils/src/os/windows.rs

## Purpose
Implements Windows disk capacity, filesystem type, volume identity, and platform-compatible stubs for mount/stat APIs.

## Important APIs, Types, And Functions
`get_info` calls `GetDiskFreeSpaceExW` and `GetDiskFreeSpaceW` to populate total/free/used bytes and cluster counts, and `get_windows_fs_type` to populate filesystem type. `get_volume_name` wraps `GetVolumePathNameW`. `same_disk` compares volume root paths. `get_physical_device_ids` returns the volume path string. `get_volume_serial_number` returns the Windows volume serial. `check_cross_device_mounts` and `get_drive_stats` are no-op/default equivalents.

## Control Flow And State
No persistent state. Path strings are converted to null-terminated UTF-16 with `to_wide_path`; unsafe Windows API calls write into stack variables and fixed `MAX_PATH` buffers. `get_info` rejects free space greater than total.

## Dependencies And Integration Points
Uses the `windows` crate and `std::os::windows::ffi::OsStrExt`. Re-exported by `os/mod.rs` on Windows for storage/disk diagnostics.

## Risks And Test Signals
Fixed `MAX_PATH` buffers can limit unusual long-path scenarios. Physical device identity is volume-based rather than true underlying disk topology. Mount validation and IO stats are placeholders. Coverage is mostly through shared OS facade tests; unsafe API paths need Windows CI to validate.
