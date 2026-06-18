# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_rb.c

Implements the red-black-tree extent backend for sparse 64-bit bitmaps. Set bits are represented as non-overlapping extents (`start`, `count`) stored in an rbtree, with read/write cursors for locality.

Core structures:
- `struct bmap_rb_extent`: rbtree node plus extent start/count.
- `struct ext2fs_rb_private`: rbtree root, write cursor, read cursor, next read cursor, optional stats counters.

Core behavior:
- `rb_insert_extent` inserts a set-bit extent, merging adjacent or overlapping neighbors.
- `rb_remove_extent` clears a range, truncating, deleting, or splitting extents.
- `rb_test_bit` checks cursor hits first, then searches the rbtree.
- `rb_set_bmap_range` converts a packed bit array into extents.
- `rb_get_bmap_range` emits packed bits from matching extents.
- `rb_find_first_zero` and `rb_find_first_set` search within inclusive bounds.
- `rb_resize_bmap` truncates extents beyond the new end and marks padding beyond logical end to real end.

The exported `ext2fs_blkmap64_rbtree` vtable implements the same `ext2_bitmap_ops` contract as the bitarray backend.

Dependencies: `ext2fsP.h`, `bmap64.h`, `rbtree.h`, raw bitops, libext2fs allocators.

Implementation notes:
- This backend is optimized for sparse maps, especially large filesystems with long runs.
- Debug-only `check_tree` validates sorted, non-overlapping, nonzero extents.
- `rb_get_new_extent` aborts on allocation failure rather than returning an error, unlike most libext2fs allocation paths.
- `rb_find_first_zero` returns `ENOENT` for an empty tree, which treats an all-zero sparse bitmap differently than the intuitive “start is zero”; callers need to account for backend semantics or generic wrappers.
