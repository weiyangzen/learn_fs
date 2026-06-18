# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-usage.c

## Purpose
Implements `btrfs filesystem usage` and shared chunk/device accounting helpers used by `btrfs device usage`.

## Chunk and Space Loading
- `load_chunk_info()` uses tree-search ioctl on the chunk tree and groups chunks by `(type, devid, num_stripes)` through `add_info_to_list()`.
- `load_space_info()` calls `BTRFS_IOC_SPACE_INFO` twice: first to get count, then to fetch and sort all space entries.
- `load_device_info()` calls `BTRFS_IOC_FS_INFO` and `device_get_info()` over device ids, skips seed devices when detectable, and records device size, filesystem-occupied size, and path/missing state.
- `load_chunk_and_device_info()` combines chunk and device loading and degrades with warnings on permission-limited chunk or FS info access.

## Accounting Logic
- `calc_chunk_size()` converts grouped chunk size to per-device allocation size, handling parity/sub-stripes and special RAID1/DUP cases.
- `get_raid56_space_info()` estimates raw chunk and used bytes for RAID5/6 using logical usage ratios and parity counts.
- `print_filesystem_usage_overall()` computes raw total size, allocated, used, unallocated, missing, slack, estimated free, minimum free, data/metadata ratios, global reserve, multiple profiles, and zoned unusable/zone size values.

## Output Modes
- Linear output prints each block-group type/profile with size, used percentage, per-device allocations, and unallocated device space.
- Tabular output builds a matrix of devices versus space-info columns, plus unallocated, total, slack, total, and used rows.
- `print_device_chunks()` and `print_device_sizes()` expose per-device output for `device usage`.

## Notable Edge Cases
RAID56 free/unallocated estimates are marked unreliable if chunk info is unavailable. Seed devices are filtered by fsid comparison through sysfs or direct superblock reads. Missing devices have zero `device_size`, contributing to missing totals.
