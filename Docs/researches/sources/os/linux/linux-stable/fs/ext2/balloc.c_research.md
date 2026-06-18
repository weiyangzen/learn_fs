# File Research: sources/os/linux/linux-stable/fs/ext2/balloc.c

## Summary
Implements ext2 block bitmap validation, block allocation/freeing, per-file reservation windows, free-block accounting, and sparse-superblock group metadata sizing.

## Main Responsibilities
- Locates group descriptors and validates block bitmap metadata bits.
- Allocates and frees data blocks while updating bitmaps, group descriptors, quotas, inode dirty state, and percpu counters.
- Maintains a filesystem-wide red-black tree of block reservation windows.
- Chooses free blocks near goals, inside reservations, or by scanning groups.
- Enforces reserved-block policy for non-privileged users.
- Reports free block counts and backup super/group-descriptor block usage.

## Key APIs
- `ext2_get_group_desc()`.
- `ext2_new_blocks()`.
- `ext2_free_blocks()`.
- `ext2_data_block_valid()`.
- `ext2_init_block_alloc_info()`, `ext2_discard_reservation()`, `ext2_rsv_window_add()`.
- `ext2_count_free_blocks()`.
- `ext2_bg_has_super()`, `ext2_bg_num_gdb()`.

## Important Behavior
Allocation starts with a goal block, maps it to a group, reads the group block bitmap, and tries to allocate near the goal. Regular files may use a reservation window if enabled. Reservation windows live in an rb-tree, grow after good hit ratios, can cross group boundaries, and are abandoned if they cause false ENOSPC.

`ext2_new_blocks()` charges quota before allocation, checks global reserved-block rules, searches the goal group first, then other groups, and falls back to no-reservation allocation before returning ENOSPC. It rejects allocations in block bitmap, inode bitmap, or inode table zones.

`ext2_free_blocks()` validates the block range, splits frees across group boundaries, rejects system-zone frees, clears bitmap bits atomically under the blockgroup lock, and updates counters only for bits that were actually set.

## State and Synchronization
Group descriptor counters are protected by per-blockgroup locks. Reservation windows are protected by `s_rsv_window_lock`. Per-superblock free block state is tracked both in group descriptors and `s_freeblocks_counter`.

## Risks
This file sits on multiple consistency boundaries: bitmap bits, group descriptor counts, percpu counters, quota state, and reservation rb-tree state must stay aligned. Corrupt metadata can trigger error paths that continue with a corrupt bitmap depending on mount error policy.
