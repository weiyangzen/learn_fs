# File Research: sources/os/linux/linux/fs/nfs/io.c

## Purpose
Implements NFS client serialization between buffered I/O and direct I/O using `inode->i_rwsem` plus the `NFS_INO_ODIRECT` inode flag.

## Key Functions
- `nfs_start_io_read()` starts buffered reads. It takes `i_rwsem` shared when already in buffered mode, or upgrades through exclusive locking to clear direct-I/O mode.
- `nfs_end_io_read()` releases the shared lock.
- `nfs_start_io_write()` starts buffered writes. It takes `i_rwsem` exclusive and blocks direct I/O by clearing `NFS_INO_ODIRECT` and waiting for in-flight DIO.
- `nfs_end_io_write()` releases the exclusive lock.
- `nfs_start_io_direct()` starts direct I/O. It takes shared locking if direct mode is already active, otherwise takes exclusive locking, sets `NFS_INO_ODIRECT`, syncs the mapping, then downgrades.
- `nfs_end_io_direct()` releases the shared lock.

## Synchronization Model
Buffered reads can run concurrently with other buffered reads. Direct I/O can run concurrently with other direct I/O. Mode transitions require exclusive `i_rwsem`. Buffered writes and truncates serialize against both read and direct paths through the write side of `i_rwsem`.

## Research Notes
This file is small but important for page-cache coherency. Its central invariant is that switching between buffered and direct paths flushes or waits at the transition while preventing concurrent mode flips.
