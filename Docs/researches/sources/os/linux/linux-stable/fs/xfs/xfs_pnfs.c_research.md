# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.c

## Purpose
Implements XFS block-layout pNFS server callbacks: lease breaking, filesystem UUID export, block mapping for clients, and block commit handling after client writes.

## Main APIs
- `xfs_break_leased_layouts` breaks pNFS layouts before operations that remove extents or need writer synchronization, upgrading from shared to exclusive IOLOCK if it must sleep.
- `xfs_fs_get_uuid` exports the filesystem UUID and its superblock offset.
- `xfs_fs_map_blocks` returns an iomap layout for direct client access and allocates blocks for write layouts when needed.
- `xfs_fs_commit_blocks` converts unwritten extents, invalidates page cache, updates timestamps and size, and commits synchronously.

## Mapping Behavior
XFS refuses pNFS layouts for shutdown filesystems, realtime inodes, and reflink inodes because clients cannot identify the realtime device and Linux block pNFS lacks reflink semantics. It serializes with local I/O, flushes and invalidates page cache, maps the requested extent, allocates holes for write layouts, logs inode preallocation/timestamp changes, forces the inode log, and returns the mount generation.

## Commit Behavior
Commit invalidates cached pages for written ranges, converts unwritten extents to written, validates any size extension lands in allocated written space, applies caller-supplied timestamp and size attributes, logs the inode core, and forces a synchronous transaction.

## Correctness Notes
The file open-codes inode modification instead of VFS file helpers because pNFS modifies inode metadata without a local file write path. The prealloc flag protects newly allocated client-write extents from reclaim before the client commits them.
