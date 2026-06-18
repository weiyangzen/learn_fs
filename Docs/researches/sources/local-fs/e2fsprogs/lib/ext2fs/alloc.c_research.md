# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc.c

## Purpose
Implements core libext2fs allocation helpers for new inodes, single blocks, block ranges, allocation callbacks, and allocation goals.

## Main Elements
- `ext2fs_clear_block_uninit()`: clears group block-uninitialized flag, updates checksum and dirty flags.
- `check_inode_uninit()`: initializes uninitialized inode bitmap groups before searching.
- `ext2fs_new_inode()`: finds the next free inode starting near parent directory’s group, wrapping around.
- `ext2fs_new_block3()` / `ext2fs_new_block2()` / `ext2fs_new_block()`: find a free block/cluster from a goal, with callback support and recursion avoidance.
- `ext2fs_alloc_block3()` / wrappers: allocate, zero, write, and account for a block.
- `ext2fs_get_free_blocks2()` / wrapper: find a free contiguous block run with bitmap granularity alignment.
- Callback setters: `ext2fs_set_alloc_block_callback()`, `ext2fs_set_new_range_callback()`.
- `ext2fs_find_inode_goal()`: derives an allocation goal from an inode’s extent, first block, or flex group.
- `ext2fs_new_range()`: finds free ranges with fixed-goal, min-length, and zeroing flags.
- `ext2fs_alloc_range()`: allocates and accounts a minimum-length range.

## Dependencies And Integration
Uses bitmap search/test APIs, group descriptor checksum helpers, extent APIs, zeroing/I/O helpers, and allocation stats from `alloc_stats.c`. Consumers include mke2fs, e2fsck repairs, inode expansion, bad-block inode updates, and other libext2fs mutators.

## Risk Notes
This code returns free locations but does not always mark them; callers must account allocations correctly. Bigalloc cluster granularity and uninitialized bitmap flags are central correctness concerns.
