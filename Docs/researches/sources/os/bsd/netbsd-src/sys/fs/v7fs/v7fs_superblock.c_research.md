# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.c

## Purpose
Implements V7FS superblock load/writeback, free-block cache refill, free-inode cache scan, and superblock/free-list endian conversion.

## Main Interfaces
- `v7fs_superblock_load()` reads sector `V7FS_SUPERBLOCK_SECTOR`, converts it, and validates core invariants.
- `v7fs_superblock_writeback()` writes modified in-memory superblock state back to disk.
- `v7fs_freeblock_update()` reads a chained free-block table and installs it into the in-memory superblock cache.
- `v7fs_freeblock_endian_convert()` converts and validates free-block table counts.
- `v7fs_freeinode_update()` scans the ilist for unallocated inodes and fills the free-inode cache.

## Implementation Notes
Sanity checks reject too-small volumes, invalid data starts, oversized free caches, impossible free counts, and unreadable final sectors. Free-inode scanning uses the on-disk inode `mode` field as the allocation test.

## Dependencies
Uses scratch I/O, endian helpers, inode helpers, datablock sanity, and `struct v7fs_superblock`.
