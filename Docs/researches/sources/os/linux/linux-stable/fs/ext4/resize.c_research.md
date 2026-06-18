# File Research: sources/os/linux/linux-stable/fs/ext4/resize.c

## Summary
Implements online ext4 filesystem growth. It validates resize requests, extends partial final groups, adds new block groups or flex groups, updates group descriptor tables and backup metadata, manages resize-inode and meta_bg transitions, initializes new group metadata, and publishes new groups safely to running allocators.

## Main Responsibilities
- Gate online resize with privilege, mount-state, primary-superblock, feature, and single-resizer checks.
- Validate geometry for newly added groups.
- Allocate metadata placement for block bitmaps, inode bitmaps, and inode tables across flex groups.
- Initialize new group metadata blocks, bitmaps, inode tables, superblock/GDT backups, and reserved GDT areas.
- Add new group descriptor blocks from the resize inode or meta_bg layout.
- Populate group descriptors and allocator group info.
- Update superblock counts, percpu counters, flex-group counters, reserved blocks, overhead, checksums, and group count with memory-ordering rules.
- Update backup superblocks and group descriptor backups after successful resize.
- Convert from resize_inode to meta_bg when reserved GDT space is exhausted.
- Support simple extension of the current last group.

## Key Data Structures
- `struct ext4_rcu_ptr`: helper wrapper for RCU-delayed freeing of replaced pointer arrays.
- `struct ext4_new_flex_group_data`: resize batch state containing group data array, per-group flags, allocated array capacity, and count.
- `struct ext4_new_group_data`: per-new-group geometry supplied by ioctl or synthesized during full resize.
- Existing superblock state: `s_group_desc`, `s_groups_count`, `s_gdb_count`, `s_flex_groups`, `s_reserved_gdt_blocks`, `s_first_meta_bg`, and ext4 free-space counters.

## Resize Entry and Exit
- `ext4_resize_begin()`: requires `CAP_SYS_RESOURCE`, checks resize_inode consistency, rejects backup-superblock mounts, error-state filesystems, sparse_super2, and concurrent resize.
- `ext4_resize_end()`: clears the resizing flag and optionally recomputes overhead.
- `ext4_resize_fs()`: high-level grow-to-size entry point. It verifies device size, cluster-aligns bigalloc requests, extends the current final group, allocates flex-group arrays, loops adding flex groups, handles resize_inode exhaustion, and reports final size.
- `ext4_group_extend()`: ioctl/remount path for extending only the current partial last group.
- `ext4_group_add()`: legacy single-group add path using caller-provided group layout.

## Group Validation and Metadata Allocation
- `verify_group_input()` checks that a new single group follows current group count and that bitmaps/inode table lie within the group without overlaps with each other or GDT/super metadata.
- `alloc_flex_gd()` sizes a flex-group work array while bounding allocation with `MAX_RESIZE_BG`.
- `ext4_alloc_group_tables()` chooses contiguous space for block bitmaps, inode bitmaps, and inode tables across a flex group, updates metadata-block accounting, adjusts uninitialized flags, and subtracts metadata from free cluster counts.
- `ext4_setup_next_flex_gd()` synthesizes the next batch of groups to add, including partial last-group handling and initial group descriptor flags.

## New Group Initialization
- `setup_new_flex_group_blocks()` journals initialization of new metadata outside the live filesystem area before publishing it. It copies backup GDT blocks, zeros reserved backup descriptor blocks and inode tables, initializes block/inode bitmaps when not uninitialized, marks unusable bitmap tails, and marks group-table blocks used in block bitmaps.
- `set_flexbg_block_bitmap()` marks metadata clusters used across possibly multiple groups, skipping uninitialized block bitmap cases when valid.
- `bclean()` obtains and zeroes a metadata block under journal write access.
- `ext4_resize_ensure_credits_batch()` extends/restarts resize transactions as metadata initialization consumes credits.

## Group Descriptor Growth
- `ext4_list_backups()` iterates groups that contain backup superblock/GDT copies for sparse, sparse_super2, and non-sparse filesystems.
- `verify_reserved_gdb()` validates that a primary reserved GDT block lists the expected backup GDT blocks.
- `add_new_gdb()` promotes a reserved GDT block from the resize inode into the active primary group descriptor array, clears its resize-inode reference, adjusts resize inode block count, decrements reserved GDT blocks, and RCU-replaces `s_group_desc`.
- `add_new_gdb_meta_bg()` adds a new descriptor block using meta_bg placement and RCU-replaces `s_group_desc`.
- `reserve_backup_gdb()` records new backup reserved GDT blocks into reserved primary GDT blocks and updates the resize inode block count.
- `ext4_add_new_descs()` coordinates descriptor-block write access, reserved backup setup, and new descriptor block addition for each new group.
- `ext4_setup_new_descs()` writes each group descriptor, sets bitmap/inode table locations, free counts, inode counts, flags, descriptor checksums, bitmap checksums, and creates allocator group info.

## Superblock and Backup Updates
- `ext4_update_super()` publishes new blocks/inodes before increasing `s_groups_count`, uses a write memory barrier before group-count publication, updates reserved/free/inode counters, flex-group counters, blockfile group limits, overhead, and superblock checksum.
- `ext4_add_overhead()` updates cached overhead and on-disk overhead clusters with ordering.
- `update_backups()` writes updated backup superblocks and descriptor blocks in backup groups, marking the filesystem invalid for fsck if backup updates fail after the live resize has succeeded.
- `ext4_set_block_group_nr()` stamps backup superblocks with their group number and checksum.

## Resize-Inode to Meta_bg Conversion
- `num_desc_blocks()` computes descriptor block count.
- `ext4_convert_meta_bg()` clears `resize_inode`, enables `meta_bg`, sets `s_first_meta_bg`, optionally frees the resize inode double-indirect block after sanity checks, and journals the superblock/inode updates.
- `ext4_resize_fs()` temporarily caps growth at available reserved GDT capacity, converts to meta_bg, then retries the original target size when necessary.

## Synchronization and Lifetime
- `EXT4_FLAGS_RESIZING` serializes online resize operations.
- Group descriptor pointer arrays are replaced with RCU assignment and freed through `ext4_kvfree_array_rcu()`.
- New group metadata is initialized before `s_groups_count` is increased, so allocators cannot see partially initialized groups.
- A write memory barrier precedes group-count publication; readers are expected to pair with read barriers after reading group count.
- Superblock buffer locking protects on-disk superblock field updates.
- Resize operations are journaled with `EXT4_HT_RESIZE`, often using credit batching for long metadata loops.

## Dependencies
Depends on ext4 group descriptor helpers, block/inode bitmap checksum helpers, multiblock allocator group-info setup, flex_bg arrays, jbd2 journaling, block zeroout, resize inode layout, meta_bg feature handling, superblock checksums, and backup-superblock enumeration.

## Risks and Edge Cases
- Online shrink is not supported.
- sparse_super2 is rejected for online resize.
- Non-sparse filesystems cannot grow past descriptor block boundaries without reserved layout support.
- Bigalloc resize targets are silently rounded down to cluster boundaries.
- If backup metadata updates fail after publishing the resize, the live filesystem remains grown but is marked invalid so fsck rewrites backups.
- Many operations are ordered to avoid rollback requirements because jbd2 cannot undo partially prepared on-disk resize metadata once dirtied.
