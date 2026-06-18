# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fallocate.c

## Role

Implements `ext2fs_fallocate`, the ext2fs library entry point for preallocating file blocks. It has a specialized extent-tree allocator for ext4 extent inodes and a slow legacy block-mapped path using `ext2fs_bmap2`.

## Main Flow

- `ext2fs_fallocate()` validates flags and length, loads the inode if the caller did not provide one, and dispatches to `extent_fallocate()` for `EXT4_EXTENTS_FL` inodes.
- `extent_fallocate()` opens an extent handle, walks mapped extents around the requested logical range, identifies holes, and calls `ext_falloc_helper()` to attach or create mappings.
- `ext_falloc_helper()` tries, in order, to fill cluster edges, merge adjacent extents, extend the left extent, extend the right extent, use implied cluster allocations, and finally allocate new extents anywhere.
- `claim_range()` updates block allocation stats and inode `i_blocks` via `ext2fs_block_alloc_stats_range()` and `ext2fs_iblk_add_blocks()`.

## Important Details

- Bigalloc cluster alignment is central. Allocation goals and range adjustments are masked by `EXT2FS_CLUSTER_MASK(fs)` and scaled with `EXT2FS_CLUSTER_RATIO(fs)`.
- Initialized extents beyond EOF are restricted unless `EXT2_FALLOCATE_INIT_BEYOND_EOF` is set.
- `EXT2_FALLOCATE_FORCE_INIT` and `EXT2_FALLOCATE_FORCE_UNINIT` are mutually exclusive and influence new extent flags.
- Zeroing is conditional on `EXT2_FALLOCATE_ZERO_BLOCKS` and initialized extent state.
- Legacy non-extent allocation maps one logical block at a time and batches zeroing of contiguous physical blocks up to 65536 blocks.

## Dependencies

Uses extent APIs (`ext2fs_extent_open2`, `ext2fs_extent_get`, `ext2fs_extent_replace`, `ext2fs_extent_insert`, `ext2fs_extent_delete`, `ext2fs_extent_fix_parents`), allocator APIs (`ext2fs_new_range`, `ext2fs_bmap2`), zeroing (`ext2fs_zero_blocks2`), bitmap/stat updates, and inode block accounting from `i_block.c`.

## Risks / Notes

- Error handling does not roll back allocations or extent edits after partial progress; callers should treat errors as potentially leaving modified filesystem state.
- The extent merge zeroing call uses `range_start` as the physical block argument in one path, while nearby zeroing paths use physical block numbers. This is worth extra review if this code is exercised.
- Non-extent fallback always zeroes newly allocated blocks even though the flags are documented for initialized/uninitialized extent behavior.
