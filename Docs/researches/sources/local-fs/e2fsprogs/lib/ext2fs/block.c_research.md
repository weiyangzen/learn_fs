# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/block.c

Implements inode block iteration for direct, indirect, double-indirect, triple-indirect, extent-based, and HURD translator blocks. The primary API is `ext2fs_block_iterate3`; older `ext2fs_block_iterate2` and `ext2fs_block_iterate` are compatibility wrappers.

The iterator callback receives filesystem, mutable block number, logical block count, referring block, reference offset, and private data. Return flags such as `BLOCK_CHANGED`, `BLOCK_ABORT`, and `BLOCK_ERROR` control mutation and traversal termination.

Traversal modes:
- Direct block array entries are visited first for classic block-mapped inodes.
- Indirect levels are handled by `block_iterate_ind`, `block_iterate_dind`, and `block_iterate_tind`.
- Extent inodes use `ext2fs_extent_open2`, `ext2fs_extent_get`, `ext2fs_extent_replace`, and `ext2fs_extent_set_bmap`.
- `BLOCK_FLAG_APPEND` visits sparse holes to allow allocation/appending.
- `BLOCK_FLAG_DEPTH_TRAVERSE` changes when metadata blocks are reported.
- `BLOCK_FLAG_DATA_ONLY` suppresses indirect/extent metadata callbacks.
- `BLOCK_FLAG_READ_ONLY` rejects callbacks that try to change blocks.

Safety behavior:
- Invalid indirect block numbers outside filesystem bounds return specific bad-indirect errors.
- Inline-data inodes return `EXT2_ET_INLINE_DATA_CANT_ITERATE`.
- `BLOCK_FLAG_NO_LARGE` rejects large non-directory old-style iteration.
- Changed indirect buffers and inode blocks are written back before return.

Implementation notes:
- The file maintains logical block count carefully across sparse indirect ranges.
- Extent traversal handles uninitialized extents and append allocation through `ext2fs_extent_set_bmap`.
- Compatibility wrappers downcast 64-bit block numbers to 32-bit callback signatures.
