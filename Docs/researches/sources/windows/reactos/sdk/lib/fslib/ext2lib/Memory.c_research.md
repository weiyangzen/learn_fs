# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Memory.c

This file contains ext2 allocation accounting, group table allocation, free block search, inode table zeroing, block allocation, directory block creation, and simple block I/O wrappers.

Core responsibilities:
- `ext2_group_of_ino` and `ext2_group_of_blk` compute owning block group.
- `ext2_inode_alloc_stats2`, `ext2_inode_alloc_stats`, and `ext2_block_alloc_stats` update bitmaps, group counters, and superblock free counts.
- `ext2_allocate_tables` initializes all group metadata locations by calling `ext2_allocate_group_table`.
- `ext2_allocate_group_table` allocates inode table, block bitmap, and inode bitmap blocks for a group.
- `ext2_get_free_blocks`, `ext2_new_block`, and `ext2_alloc_block` locate and allocate free blocks.
- `write_inode_tables` zeroes all inode table blocks.
- `ext2_new_dir_block` creates a directory block with `.` and `..` entries.
- `ext2_read_block` and `ext2_write_block` wrap raw disk I/O at filesystem block granularity.

Important behavior:
- Inode tables are allocated first, then bitmap blocks.
- Optional `stride` changes bitmap placement to spread metadata.
- Block allocation zeroes the newly allocated block before updating allocation statistics.

Risk points:
- Allocation search is linear and simple.
- `ext2_get_free_blocks` treats `ext2_test_block_bitmap_range` truth as availability, so correctness depends on bitmap helper semantics.
- Counter updates subtract `inuse`; negative or mismatched callers can silently skew counts.
- `write_inode_tables` uses the static zero buffer in `zero_blocks` and then explicitly frees it with `zero_blocks(NULL, ...)`.
