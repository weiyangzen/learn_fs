# File Research: sources/teaching/minix/minix/fs/ext2/balloc.c

This file implements ext2 block allocation, block freeing, and inode-local block preallocation.

Key entry points:
- `discard_preallocated_blocks(struct inode *rip)`: frees preallocated blocks either for one inode or globally across the in-core inode table.
- `alloc_block(struct inode *rip, block_t block)`: allocates a data block near a caller-provided goal or near the inode’s block group.
- `free_block(struct super_block *sp, bit_t bit_returned)`: clears a block bitmap bit, updates free counters, and tells libminixfs/VM that the block is no longer associated with an inode.
- Internal `alloc_block_bit()` scans group block bitmaps, optionally allocating an entire byte for `EXT2_PREALLOC_BLOCKS`.

Important behavior:
- Honors read-only mounts by panicking on attempted metadata mutation.
- Avoids reserved blocks unless `opt.use_reserved_blocks` is set.
- Discards all preallocations when free space is low.
- Maintains `s_free_blocks_count`, group `free_blocks_count`, `lmfs_change_blockusage`, `group_descriptors_dirty`, and `s_bsearch`.
- `check_block_number()` prevents allocation/freeing of group metadata blocks such as bitmaps and inode tables.

Dependencies:
- Uses `get_group_desc`, `get_block`, `setbit`, `setbyte`, `unsetbit`, `lmfs_markdirty`, `lmfs_free_block`.
- Depends heavily on `struct super_block`, `struct inode`, and bitmap accessor macros from `buf.h`.

Notable risks:
- Several allocator invariants panic rather than recover.
- Preallocation depends on `EXT2_PREALLOC_BLOCKS == CHAR_BIT`; this is asserted.
- `setbyte()` allocation starts from the beginning of a bitmap rather than the requested goal word, so preallocation locality is coarser than normal `setbit()` allocation.
