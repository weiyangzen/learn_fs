# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.h

## Purpose
Defines the in-memory V7FS inode and declares inode allocation, disk I/O, validation, utility, and ilist iteration functions.

## Main Interfaces
- `struct v7fs_inode` stores inode number, mode/link/owner/time attributes, append flag, special-device number, file size, and V7 address array.
- Macros classify V7 original, 2BSD extension, and NetBSD FIFO inode types.
- Declares allocate/deallocate, load/writeback, disk-to-memory conversion, `v7fs_inode_chmod()`, `v7fs_inode_dump()`, and `v7fs_ilist_foreach()`.

## Dependencies
Requires V7FS mode constants, address counts, and on-disk inode structures from `v7fs.h`.
