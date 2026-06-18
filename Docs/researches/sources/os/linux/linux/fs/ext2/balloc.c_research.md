# File Research: sources/os/linux/linux/fs/ext2/balloc.c

Read status: complete, 1535 lines.

This file implements ext2 block bitmap handling, block allocation, block freeing, free-space accounting, and reservation-window management.

Key responsibilities:
- Retrieves and validates block group descriptors with `ext2_get_group_desc()`.
- Reads and validates per-group block bitmaps, ensuring metadata blocks are marked allocated.
- Frees data blocks with `ext2_free_blocks()`, including group-boundary splitting, system-zone checks, bitmap clearing, descriptor updates, quota freeing, and percpu free-block counter updates.
- Allocates blocks with `ext2_new_blocks()`, using goal-directed allocation, bitmap scans, group fallback, quota charging, reserved-block policy, and optional reservation windows.
- Manages reservation windows for regular files using an RB tree rooted in `s_rsv_window_root`.
- Counts free blocks and computes sparse-super/group-descriptor block usage.

Reservation-window design:
- Each regular file may lazily receive `ext2_block_alloc_info`, which contains a reservation-window node and last allocation hints.
- Reservation windows are inserted into an RB tree ordered by filesystem block range.
- Allocation first tries an existing suitable reservation, otherwise finds a new reservable gap near the goal.
- Window size can grow based on hit rate and requested allocation size, capped by `EXT2_MAX_RESERVE_BLOCKS`.
- Reservation can be disabled globally with mount option state or per inode by setting reservation size to zero.

Allocation flow:
- Quota is charged up front with `dquot_alloc_block()`.
- `ext2_has_free_blocks()` enforces reserved-block policy for non-privileged users.
- The allocator starts in the goal group, then scans other groups, skipping groups with no free blocks or insufficient space for reservations.
- If reservations falsely cause ENOSPC, allocation retries without reservation.
- Successful allocation marks bitmap buffers dirty, updates group descriptor counts, subtracts percpu free blocks, and adjusts quota if fewer blocks were allocated than requested.

Safety and validation:
- `ext2_valid_block_bitmap()` checks block bitmap, inode bitmap, and inode table bits.
- `ext2_data_block_valid()` rejects ranges outside the data zone, wrapping ranges, ranges past `s_blocks_count`, and ranges overlapping the superblock.
- Allocation and free paths reject block ranges that overlap block bitmap, inode bitmap, or inode table.
- Per-block-group bitmap mutation uses block-group locks.
- Reservation tree mutation uses `s_rsv_window_lock`.

External dependencies:
- Uses buffer heads, quota operations, capabilities, percpu counters, blockgroup locks, and RB trees.
- Called heavily from `inode.c` when mapping file blocks.

Research notes:
- This is the core ext2 free-space allocator.
- It combines old bitmap allocation with preallocation-like reservation windows for better locality in growing regular files.
- Metadata consistency is maintained manually through bitmaps, group descriptors, superblock-level counters, and quota state.
