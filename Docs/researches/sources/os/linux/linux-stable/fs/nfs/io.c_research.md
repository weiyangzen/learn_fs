# File Research: sources/os/linux/linux-stable/fs/nfs/io.c

## Purpose
Implements NFS client I/O mode serialization between buffered I/O and direct I/O using `inode->i_rwsem` plus the `NFS_INO_ODIRECT` inode flag.

## Key Functions
- `nfs_start_io_read(struct inode *inode)`
  - Starts buffered read.
  - Takes `i_rwsem` for read when no direct I/O mode is active.
  - If direct mode is active, upgrades through a write lock, calls `nfs_file_block_o_direct()`, then downgrades to read lock.
- `nfs_end_io_read(struct inode *inode)`
  - Releases read side of `i_rwsem`.
- `nfs_start_io_write(struct inode *inode)`
  - Starts buffered write.
  - Takes `i_rwsem` for write and blocks direct I/O via `nfs_file_block_o_direct()`.
  - Exported GPL.
- `nfs_end_io_write(struct inode *inode)`
  - Releases write side of `i_rwsem`.
  - Exported GPL.
- `nfs_start_io_direct(struct inode *inode)`
  - Starts direct I/O.
  - Takes shared lock if `NFS_INO_ODIRECT` already set.
  - Otherwise takes write lock, sets `NFS_INO_ODIRECT`, syncs mapping via `nfs_sync_mapping()`, and downgrades to shared lock.
- `nfs_end_io_direct(struct inode *inode)`
  - Releases read side of `i_rwsem`.

## Synchronization Model
- Buffered reads and direct I/O can each run concurrently with same-mode operations under shared `i_rwsem`.
- Mode transitions require exclusive `i_rwsem`.
- Buffered writes and truncates are serialized with both buffered reads and direct I/O by taking the write side.
- `NFS_INO_ODIRECT` marks direct-I/O mode; clearing it waits for in-flight direct I/O through `inode_dio_wait()` in the header helper.

## Research Notes
This file is small but critical to page-cache coherency. The main invariant is that switching between buffered and direct paths flushes/waits at the transition point while preventing concurrent mode flips.
