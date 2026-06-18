# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_readwrite.c

This file implements UFS read/write operations for FFS through macro aliases. Regular files use UBC/page-cache I/O; directories and long symlinks use buffer-cache I/O.

Key responsibilities:
- Read regular files via `ubc_uiomove`.
- Read directories and long symlinks through filesystem block reads.
- Write regular files through UBC with block allocation and WAPBL transaction coverage.
- Write directories and long symlinks through buffer-cache allocation and `uiomove`.
- Update access/change/modify times and clear setuid/setgid bits after writes.
- Roll back file size and `uio` state on write errors.

Important functions:
- `ffs_read` via `READ`: Validates read state, dispatches directories to `BUFRD`, handles snapshots, bounds reads by inode size, supports direct I/O hints, and updates atime.
- `ffs_bufrd` via `BUFRD`: Buffer-cache read path with block mapping, one-block readahead, residual protection, and `uiomove`.
- `ufs_post_read_update`: Marks `IN_ACCESS` unless `MNT_NOATIME`; performs synchronous metadata update for `IO_SYNC`.
- `ffs_write` via `WRITE`: Handles append mode, append-only enforcement, maximum size, WAPBL transaction scope, fragment expansion, block/page allocation, UBC writes, page flushing, and final metadata update.
- `ffs_bufwr` via `BUFWR`: Writes directory/symlink data through `UFS_BALLOC`, updates inode size, invalidates leaked buffers on failed partial writes, and chooses sync/async/delayed writeback.
- `ufs_post_write_update`: Marks ctime/mtime and relatime atime, clears privileged mode bits if credentials lack retention authority, truncates back on error, restores `uio` state, and syncs metadata for `IO_SYNC`.

Important interactions:
- Uses FFS block macros (`ffs_lblkno`, `ffs_blksize`, etc.) through local macro aliases.
- Regular-file allocation uses `ufs_balloc_range` and `GOP_ALLOC`; buffer paths use `UFS_BALLOC`.
- WAPBL transaction coverage is intentionally broad for regular-file writes that allocate blocks.

Notable behavior and risks:
- The write path explains why WAPBL currently forces large single transactions for writes that may allocate blocks.
- On failed writes, `UFS_TRUNCATE` restores the original file size and rewinds the caller’s `uio`.
- Directory writes require `IO_SYNC`, exclusive vnode locking, and an already-held journal lock.
