# File Research: sources/os/linux/linux-stable/fs/remap_range.c

## Purpose
Implements generic VFS preparation and validation for file range remapping, reflink/clone, and deduplication.

## Main Responsibilities
- `generic_remap_checks()`: validates block alignment, offset overflow, EOF handling, write limits, block-aligned length, overlap rules, and shortening policy.
- `remap_verify_area()`: validates range signs/overflow, LSM permissions, and fsnotify area permissions.
- `generic_remap_check_len()`: prevents partial EOF block remaps into invalid destination positions, shortening when allowed.
- Dedupe comparison helpers read and lock folios from source/destination and compare bytes safely.
- `__generic_remap_file_range_prep()`: performs common clone/dedupe checks, waits for direct I/O, flushes dirty ranges, verifies dedupe equality, checks final length, and calls `file_modified()` for clone/remap writes.
- `generic_remap_file_range_prep()`: public wrapper without DAX ops.
- `vfs_clone_file_range()`: same-superblock reflink entry point using filesystem `remap_file_range`.
- `vfs_dedupe_file_range_one()` and `vfs_dedupe_file_range()`: per-destination and multi-destination dedupe APIs.

## Dedupe Rules
- Source file must be readable and regular.
- Destination must pass write permission or ownership/admin checks.
- Source and destination must be on the same superblock.
- Data must compare identical; mismatches report `FILE_DEDUPE_RANGE_DIFFERS`.
- Single dedupe requests are capped at 1 GiB.

## Edge Cases
- Rejects immutable outputs and swapfiles.
- Rejects directories and non-regular files.
- DAX dedupe comparison is supported only if DAX read ops are supplied.
- Zero-length clone to EOF is expanded; zero-length dedupe returns immediately.
