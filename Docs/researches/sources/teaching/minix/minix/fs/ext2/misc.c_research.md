# File Research: sources/teaching/minix/minix/fs/ext2/misc.c

This file implements ext2 sync.

Key entry point:
- `fs_sync()`: flushes dirty in-core inodes, flushes all LMFS buffers, updates superblock write time, and writes superblock/group descriptors.

Important ordering:
- Inodes are written before `lmfs_flushall()` because `rw_inode()` leaves updates in the block cache.
- Superblock write happens after buffer flushing if the device is still mounted.

Read-only behavior:
- Returns immediately on read-only filesystems.
