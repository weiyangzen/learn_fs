# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_vnops.c

Purpose: Provides vnode-backed `fileops` and common vnode helpers for open, close, read, write, stat, ioctl, locking, seeking, and kernel read/write operations.

Key behavior:
- Defines `vnops`, the file operation table used by vnode-backed file descriptors.
- `vn_open()` validates open flags, configures `nameidata`, creates regular files when needed, checks read/write permissions, handles truncation, calls `VOP_OPEN()`, resolves cloned vnodes, and increments `v_writecount`.
- `vn_writechk()` rejects writes to read-only filesystem regular/directory/symlink vnodes and blocks writes to active text vnodes that cannot be uncached.
- `vn_fsizechk()` enforces `RLIMIT_FSIZE`, trims partial writes below the limit, and signals `SIGXFSZ` when needed.
- `vn_close()` decrements write counts, locks, calls `VOP_CLOSE()`, and releases the vnode.
- `vn_rdwr()` packages kernel I/O into a single-iovec `uio` and calls `VOP_READ()` or `VOP_WRITE()`.
- `vn_read()` and `vn_write()` handle file offsets, append behavior, nonblocking/sync flags, directory read rejection, and VOP I/O dispatch.
- `vn_stat()` converts `vattr` into user-visible `struct stat`, including vnode type to `S_IF*` mode translation.
- `vn_ioctl()` implements regular/directory `FIONREAD`, forwards FIFO/device ioctls, and updates session controlling tty on `TIOCSCTTY`.
- `vn_lock()` wraps `VOP_LOCK()` with vnode teardown awareness via `VXLOCK`, `VXWANT`, `v_lockcount`, and retry semantics.
- `vn_closefile()` releases flock-style locks before closing; `vn_kqfilter()` and `vn_seek()` provide kqueue and seek support.

Filesystem relevance:
- This is the bridge between descriptor-level file operations and filesystem-specific vnode operations.
- It centralizes offset accounting, write safety, close semantics, and stat conversion used by all VFS-backed file descriptors.
