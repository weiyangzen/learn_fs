# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock_util.c

## Purpose
Provides status/statistics calculation and diagnostic superblock dumping.

## Main Interfaces
- `v7fs_superblock_status()` populates `fs->stat` with total/free block and inode counts plus total file count.
- `v7fs_superblock_dump()` prints key superblock fields and, in userland, the update time as text.

## Dependencies
Uses `V7FS_MAX_INODE()`, `struct v7fs_superblock`, `struct v7fs_stat`, and debug printing macros.
