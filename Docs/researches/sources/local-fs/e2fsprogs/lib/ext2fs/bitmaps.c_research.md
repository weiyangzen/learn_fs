# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitmaps.c

## Purpose
Allocates, frees, copies, clears, resizes, compares, and accesses ext2fs inode/block bitmaps, including 64-bit and subcluster variants.

## Main Elements
- Free/copy/padding wrappers: `ext2fs_free_inode_bitmap()`, `ext2fs_free_block_bitmap()`, `ext2fs_copy_bitmap()`, `ext2fs_set_bitmap_padding()`.
- `ext2fs_allocate_inode_bitmap()`: allocates inode bitmap over inode range, using 64-bit backend when enabled or legacy bitmap when possible.
- `ext2fs_allocate_block_bitmap()`: allocates per-cluster block bitmap for normal block allocation, respecting bigalloc cluster conversion.
- `ext2fs_allocate_subcluster_bitmap()`: allocates true per-block bitmap for metadata tracking on bigalloc filesystems.
- `ext2fs_get_bitmap_granularity()`: reports cluster bits for 64-bit bitmaps.
- Fudge/clear/resize wrappers: adjust bitmap end ranges, clear maps, resize legacy and 64-bit maps.
- Compare wrappers: block and inode bitmap equality checks with specific error codes.
- Range access wrappers: set/get inode and block bitmap ranges for legacy and 64-bit APIs.

## Dependencies And Integration
Wraps generic bitmap and generic 64-bit bitmap implementations (`gen_bitmap`, `gen_bitmap64`, `bmap64`). Called by e2fsck, mke2fs, allocation code, bitmap I/O, and metadata repair logic.

## Risk Notes
`ext2fs_allocate_block_bitmap()` is per-cluster for backward compatibility, while `ext2fs_allocate_subcluster_bitmap()` is per-block. Callers must choose correctly, especially with bigalloc, or metadata block tracking and allocation accounting can diverge.
