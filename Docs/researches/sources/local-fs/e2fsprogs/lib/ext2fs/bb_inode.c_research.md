# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bb_inode.c

## Purpose
Updates the ext bad block inode (`EXT2_BAD_INO`) to match a bad block list.

## Main Elements
- `struct set_badblock_record`: state for iterating old/new bad block inode blocks, saved indirect blocks, buffer, and error propagation.
- `ext2fs_update_bb_inode()`: clears old bad block inode blocks, appends new bad blocks, updates inode timestamps, block count, size, and writes the inode.
- `clear_bad_block_proc()`: block iterator callback that validates old block numbers, saves indirect blocks, frees existing blocks from allocation stats, and clears block pointers.
- `set_bad_block_proc()`: block iterator append callback that consumes bad block list entries for data blocks, reuses or allocates indirect blocks, zeroes indirect blocks, marks allocations, and installs block pointers.

## Dependencies And Integration
Uses badblocks iterators, block iteration, block allocation/free stats, inode read/write, time helpers, zeroed block buffer, and I/O channel writes. It is called when mke2fs/e2fsck need to persist bad block information into the filesystem.

## Risk Notes
The file header warns that errors can leave the bad block inode inconsistent. The algorithm temporarily frees old bad-block inode blocks before fully installing the new list; error handling preserves process return status but not transactional rollback.
