# File Research: sources/os/linux/linux-stable/fs/quota/quota_v2.c

## Purpose
Implements VFS quota format v2 support for `QFMT_VFS_V0` and `QFMT_VFS_V1`, using the shared quota tree code.

## Format Variants
- v2r0: 32-bit inode/block limits, 64-bit current space and timers.
- v2r1: 64-bit limits/counts with an explicit pad field.
Both store block limits in 1 KiB quota blocks and convert to byte-based in-memory accounting.

## Main Responsibilities
- Validate quota file magic/version in `v2_check_quota_file()`.
- Read and write file info header in `v2_read_file_info()` and `v2_write_file_info()`.
- Allocate and initialize `qtree_mem_dqinfo` with block count, free block pointers, free-entry pointer, block size, tree depth, entry size, and format-specific callbacks.
- Convert disk quota records through v2r0/v2r1 `disk2mem`, `mem2disk`, and `is_id` callbacks.
- Delegate dquot read/write/release/iteration to `quota_tree.c`.

## Key Functions
- `v2_read_dquot()`
- `v2_write_dquot()`
- `v2_release_dquot()`
- `v2_get_next_id()`
- `v2_free_file_info()`

## Corruption Checks
`v2_read_file_info()` verifies that declared block counts and free-list pointers fit the quota file size and block range. Invalid metadata returns `-EUCLEAN`.

## Registration
Registers both v2r0 and v2r1 quota format descriptors with shared `v2_format_ops`.
