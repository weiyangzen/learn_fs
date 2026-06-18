# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.h

## Purpose
Declares V7FS superblock core and utility routines.

## Main Interfaces
- Core declarations cover load, writeback, free-block update/conversion, and free-inode cache refill.
- Utility declarations cover status computation and debug dumping.

## Dependencies
Requires `struct v7fs_self`, `struct v7fs_freeblock`, and V7FS on-disk constants from core headers.
