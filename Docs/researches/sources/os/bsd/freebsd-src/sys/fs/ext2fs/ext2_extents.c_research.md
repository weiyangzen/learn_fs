# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.c

This file implements FreeBSD ext4 extent tree support for ext2fs: extent validation, lookup, caching, insertion, tree splitting/growth, allocation, mapping support, and truncation/removal.

Key responsibilities:
- Initialize inode extent roots and cache state.
- Decode/store physical block fields in extent and index entries.
- Validate extent headers, extents, indexes, block ranges, ordering, and checksums.
- Find the path to an extent through root and index blocks.
- Cache mapped extents.
- Insert new extents, merge adjacent extents, correct parent indexes, split full leaves/indexes, and grow tree depth.
- Allocate extent metadata and data blocks.
- Remove extent ranges during truncation and free empty leaf/index blocks.
- Optionally print/walk extent trees under `EXT2FS_PRINT_EXTENTS`.

Important functions:
- `ext4_ext_tree_init`, `ext4_ext_in_cache`, `ext4_ext_find_extent`, `ext4_ext_path_free`.
- `ext4_ext_check_header`, `ext4_validate_extent_entries`, `ext4_ext_binsearch_index`, `ext4_ext_binsearch_ext`.
- `ext4_ext_dirty`, `ext4_ext_insert_index`, `ext4_ext_split`, `ext4_ext_grow_indepth`, `ext4_ext_create_new_leaf`.
- `ext4_ext_insert_extent`, `ext4_new_blocks`, `ext4_ext_get_blocks`.
- `ext4_ext_remove_space`, `ext4_ext_rm_leaf`, `ext4_ext_rm_index`, `ext4_read_extent_tree_block`.

Important interactions:
- Called by `ext2_balloc.c`, `ext2_bmap.c`, `ext2_inode.c`, and inode allocation.
- Uses `ext2_alloc`, `ext2_alloc_meta`, `ext2_blkfree`, `ext2_update`, and extent checksum helpers.
- Maintains `ip->i_ext_cache` and inode `IN_E4EXTENTS` state.

Notable limitations and risks:
- `ext4_new_blocks` only allocates a single block; multi-block requests currently fail to allocate as a run.
- Removal supports tail cleanup and whole extent removal but rejects middle/head-only cases.
- Extent metadata is copied into path-owned memory and written back explicitly through `ext4_ext_dirty`.
