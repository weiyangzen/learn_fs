# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.c

## Purpose
Implements V7FS inode allocation/freeing, inode disk-location calculation, and conversion between memory and on-disk inode images.

## Main Interfaces
- `v7fs_inode_number_sanity()` validates inode numbers against the superblock-derived inode count.
- `v7fs_inode_allocate()` draws from the superblock free-inode cache, refreshing it with `v7fs_freeinode_update()` as needed.
- `v7fs_inode_deallocate()` zeroes the inode on disk and returns its number to the free-inode accounting/cache.
- `v7fs_inode_load()` and `v7fs_inode_writeback()` read/write a single inode through the ilist sector area.
- `v7fs_inode_setup_memory_image()` expands disk fields, including 24-bit addresses, into `struct v7fs_inode`.

## Implementation Notes
Inode numbers start at 1. Disk location is computed from `(ino - 1) * sizeof(struct v7fs_inode_diskimage)` relative to `V7FS_ILIST_SECTOR`. Character/block device inodes copy `addr[0]` into `device`.

## Dependencies
Uses superblock free-inode state, endian macros, scratch buffers, ilist locks, and V7FS on-disk inode layout.
