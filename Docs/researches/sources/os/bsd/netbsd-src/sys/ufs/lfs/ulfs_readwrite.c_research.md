# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_readwrite.c

Read completely: 572 lines.

Implements LFS read and write vnode operations using ULFS-derived logic, with UBC for regular files and buffer-cache paths for directories, long symlinks, and the LFS ifile.

Read path:
- `lfs_read()` handles regular file reads through UBC, rejects offsets beyond max file size, handles EOF/resid zero cases, and sends directory reads and ifile reads to `lfs_bufrd()`.
- `lfs_bufrd()` reads directory/long-symlink/ifile data through `bread()`/`breadn()`, computes logical block and transfer sizes, avoids copying short-read garbage, and releases buffers.
- `ulfs_post_read_update()` marks access time unless `MNT_NOATIME` is set and forces `lfs_update()` for synchronous reads.

Write path:
- `lfs_write()` handles regular file writes through UBC.
- Enforces append-only behavior, max file size, ifile write prohibition, and zero-length no-op.
- Forces `async = true`, waits for LFS availability with `lfs_availwait()`, and checks the vnode.
- Expands trailing fragments when extending across block boundaries using `ulfs_balloc_range()`.
- Chooses between safe allocation with page initialization and overwrite allocation with `GOP_ALLOC()`.
- Copies data with `ubc_uiomove()`, updates UVM vnode size, and flushes pages for synchronous writes.
- `lfs_bufwr()` writes directories and long symlinks through buffer cache, reserves space, allocates blocks with `lfs_balloc()`, updates size, writes buffers, and unreserves on exit.

Post-write handling:
- `ulfs_post_write_update()` marks ctime/mtime and relatime atime.
- Clears setuid/setgid bits after successful writes unless authorization allows retaining them.
- On write error, truncates back to original size and restores the caller's uio offset/resid.
- On synchronous successful writes, calls `lfs_update(... UPDATE_WAIT)`.
- Asserts vnode UVM size and inode size agree.

Risks and notes:
- Comments call out legacy/temporary issues: directory reads from userland, ifile buffer I/O, and simplistic async flushing.
- Regular file writes explicitly deny writes to the ifile even if flags are altered.
- Buffer-cache write path asserts directories are written synchronously and that no pages are cached for these vnode types.
- Correctness relies on `ulfs_balloc_range()` avoiding stale block exposure for holes and partial-block writes.
