# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_stats.c

## Purpose
Updates allocation bitmaps, group descriptor counters, superblock counters, checksums, dirty flags, and optional callbacks when inodes or blocks are allocated or freed.

## Main Elements
- `ext2fs_inode_alloc_stats2()` / wrapper: marks/unmarks inode bitmap, adjusts free inode and directory counts, clears inode-uninit flag, adjusts unused-inode hint, updates checksum, and marks metadata dirty.
- `ext2fs_block_alloc_stats2()` / wrapper: marks/unmarks block bitmap, adjusts free block counters with cluster ratio, clears block-uninit flag, updates checksum, marks dirty, and invokes callback.
- `ext2fs_set_block_alloc_stats_callback()`: installs single-block stats callback.
- `ext2fs_block_alloc_stats_range()`: marks/unmarks a block range, splits accounting across groups, adjusts free counters and checksums, and invokes range callback.
- `ext2fs_set_block_alloc_stats_range_callback()`: installs range stats callback.

## Dependencies And Integration
Called by allocation/freeing paths across libext2fs and e2fsck, including bad-block inode updates and orphan cleanup. Depends on valid loaded bitmaps and group descriptors.

## Risk Notes
The `inuse` parameter is signed and used directly in counter arithmetic. Incorrect sign or cluster-alignment assumptions can corrupt free counts. Range accounting normalizes `inuse` to +/-1 and divides group counts by cluster ratio.
