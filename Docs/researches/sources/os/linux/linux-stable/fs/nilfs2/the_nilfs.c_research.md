# File Research: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.c

## Purpose
Implements allocation, initialization, loading, recovery, superblock validation, disk layout setup, segment discard/free-space accounting, and checkpoint-root lookup/lifetime for the shared `struct the_nilfs` object.

## Main Lifecycle
- `alloc_nilfs(struct super_block *sb)` allocates and initializes `struct the_nilfs`, locks, rb-tree roots, lists, counters, mount state defaults, and device pointers.
- `destroy_nilfs(struct the_nilfs *nilfs)` releases loaded superblock buffers if initialized and frees the object.
- `init_nilfs(struct the_nilfs *nilfs, struct super_block *sb)` reads superblocks, validates compatibility, determines block size, stores disk layout, initializes log cursor state, and marks the object initialized.
- `load_nilfs(struct the_nilfs *nilfs, struct super_block *sb)` searches for a super root, loads metadata files, creates sysfs device state, and performs roll-forward recovery when required.

## Superblock Handling
- `nilfs_valid_sb()` validates magic, superblock byte size, and CRC.
- `nilfs_load_super_block()` reads primary and secondary superblocks, chooses the newer valid one, rejects bad secondary offsets, and records protected sequence state from the older valid superblock.
- `nilfs_fall_back_super_block()` promotes the secondary superblock to primary.
- `nilfs_swap_super_block()` swaps primary and secondary buffer/data pointers.
- `nilfs_release_super_block()` drops both superblock buffers.

## Disk Layout and Limits
- `nilfs_get_blocksize()` derives block size from `s_log_block_size` and rejects values above `NILFS_MAX_BLOCK_SIZE`.
- `nilfs_store_disk_layout()` validates revision, superblock size, inode size, first user inode, blocks per segment, reserved-segment percentage, segment count, and device size coverage.
- `nilfs_max_size()` combines page-cache and bmap key limits for `sb->s_maxbytes`.
- `nilfs_nrsvsegs()` computes reserved segments from `ns_r_segments_percentage` with a `NILFS_MIN_NRSVSEGS` lower bound.
- `nilfs_set_nsegments()` stores total and reserved segment counts.

## Load and Recovery Flow
`load_nilfs()`:
1. Detects whether the filesystem is clean via `nilfs_valid_fs()`.
2. Searches the latest super root.
3. If search returns `-EINVAL`, may copy the spare superblock into the primary slot and retry from an earlier cursor.
4. Loads DAT, checkpoint file, and segment-usage file through `nilfs_load_super_root()`.
5. Creates the NILFS sysfs device group.
6. If recovery is needed, handles readonly and `NORECOVERY` rules, possibly temporarily clearing `SB_RDONLY`.
7. Runs `nilfs_salvage_orphan_logs()`.
8. Marks the mount state clean and calls `nilfs_cleanup_super()`.
9. Restores original mount flags.

On failure after sysfs creation, it deletes the sysfs device group and drops metadata inodes.

## Segment and Space Operations
- `nilfs_discard_segments()` batches contiguous segment ranges and issues `blkdev_issue_discard()` in device sectors.
- `nilfs_count_free_blocks()` multiplies clean segment count by blocks per segment.
- `nilfs_near_disk_full()` compares clean segments against reserved segments plus in-progress dirty block demand.

## Checkpoint Root Tree
- `nilfs_lookup_root()` searches the rb-tree by checkpoint number and increments the root refcount.
- `nilfs_find_or_create_root()` creates a new `nilfs_root`, initializes counters, inserts it into the rb-tree, and creates its sysfs snapshot group.
- `nilfs_put_root()` decrements refcount, erases the rb-tree node, removes sysfs snapshot state, drops `ifile`, and frees the root.

## Locking
- `ns_last_segment_lock` protects last written segment cursor fields.
- `ns_sem` protects shared superblock and mount state fields.
- `ns_segctor_sem` protects log writer state outside initialization.
- `ns_cptree_lock` protects the checkpoint root rb-tree and refcount transition to deletion.

## Research Notes
This file is the central shared-device state manager for NILFS2. It coordinates on-disk superblock selection, metadata inode loading, recovery policy, and sysfs attachment. The notable lifetime dependency is that `nilfs_find_or_create_root()` inserts the new root before creating its sysfs snapshot group; if sysfs creation fails, the object is freed without removing the inserted rb-node, which is a detail worth checking against current upstream history if auditing for bugs.
