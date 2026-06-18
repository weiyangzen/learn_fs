# File Research: sources/local-fs/e2fsprogs/e2fsck/emptydir.c

## Purpose
Appears intended to detect and remove empty directory blocks by compacting directory block mappings.

## Main Behavior
- Defines `empty_dir_info_struct` with a dblist, block bitmap of empty directory blocks, inode bitmap of affected directories, a block buffer, current inode/inode data, logical block counter, and freed block count.
- `init_empty_dir()` allocates the state, dblist, empty-block bitmap, and directory inode map.
- `add_empty_dirblock()` records empty directory blocks except inode 11, usually `lost+found`.
- `empty_pass1()` uses `ext2fs_bmap2()` to skip empty blocks and rewrite block references.
- `fix_directory()` reads an inode, iterates blocks with `empty_pass1()`, and adjusts size/block counts if blocks were freed.
- `process_empty_dirblock()` is meant to allocate block buffer, iterate the dblist, and free state.

## Integration
This file is not included in the main `OBJS` list in `Makefile.in`.

## Risks / Notes
The file appears stale/incomplete as read:
- `init_empty_dir()` checks `retval` immediately after `e2fsck_allocate_memzero()` even though `retval` has not been assigned by that call.
- `process_empty_dirblock()` uses undeclared `retval`.
- `process_empty_dirblock()` calls `ext2f_get_mem`, which appears to be a typo for an ext2fs/e2fsck allocator.
These issues explain why it is likely not built into the normal checker.
