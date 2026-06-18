# File Research: sources/local-fs/reiserfsprogs/fsck/ubitmap.c

`ubitmap.c` contains bitmap and allocation helpers used while rebuilding the tree.

Key responsibilities:
- Tests and marks blocks in `fsck_new_bitmap(fs)`, the bitmap representing blocks used by the rebuilt tree.
- Prevents duplicate block use with hard failures in `mark_block_used()` and `mark_block_free()`.
- Represents uninsertable leaves by clearing bits in `fsck_uninsertables(fs)`.
- Allocates new blocks through `reiserfsck_reiserfs_new_blocknrs()` using the allocable bitmap prepared by pass 1.
- Returns new buffer heads for newly allocated blocks with `reiserfsck_get_new_buffer()`.
- Frees blocks from the new bitmap and returns them to the allocable pool.

Important exported helpers:
- `is_block_used()`
- `mark_block_used()`
- `is_block_uninsertable()`
- `mark_block_uninsertable()`
- `reiserfsck_reiserfs_new_blocknrs()`
- `reiserfsck_get_new_buffer()`
- `reiserfsck_reiserfs_free_block()`

Dependencies and data flow:
- Consumes allocation helpers from `pass0.c`: `are_there_allocable_blocks()`, `alloc_block()`, and `make_allocable()`.
- Consumes `fsck_new_bitmap(fs)`, `fsck_uninsertables(fs)`, and `fsck_allocable_bitmap(fs)` created by pass 1/load routines.
- Supplies allocator hooks assigned to `fs->block_allocator` and `fs->block_deallocator`.

Notable behavior:
- Block 0 is ignored by `mark_block_used()`.
- `reiserfsck_get_new_buffer()` does not zero the buffer; callers that need zero-filled blocks explicitly clear it.
- The file comments document the rebuild model: old disk bitmap is scanned, new bitmap tracks the emerging tree, and allocable bitmap tracks blocks safe for repair allocations.
