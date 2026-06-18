# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vnops.c

Purpose: Implements FUSE filesystem vnode operations by translating VFS operations into `fusebuf` daemon requests.

Key behavior:
- Defines `fusefs_vops`, covering lookup, create, mknod, open, close, access, getattr, setattr, read, write, ioctl, kqfilter, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, inactive, reclaim, locks, strategy, print, pathconf, and advisory locking.
- Kqueue filters report read availability from cached file size, write readiness, vnode events, EOF, and revoke handling.
- `fusefs_open()` maps access mode to one of three local FUSE handle slots, uncaches UVM pages for regular files, strips create/exclusive/truncate flags, and sends open/opendir if needed.
- `fusefs_close()` sends optional `FBT_FLUSH` for writable file descriptors and caches `ENOSYS` as unsupported.
- `fusefs_access()` enforces `allow_other`, session liveness, read-only write restrictions, daemon-backed getattr, and `vaccess()`.
- `fusefs_getattr()` returns dummy root-like attributes for disallowed users, otherwise sends `FBT_GETATTR` and converts daemon `struct stat` to `vattr`, normalizing block size/block count.
- `fusefs_setattr()` validates allowed attributes, rejects flags and illegal fields, handles read-only checks, sends `FBT_SETATTR`, caches unsupported setattr, updates UVM size on truncate, and emits attribute knotes.
- Namespace operations send daemon requests for link, symlink, create/mknod, rename, mkdir, rmdir, and unlink, with `UNDEF_*` operation caching, name buffer cleanup, vnode notifications, and VFS locking/release conventions.
- `fusefs_readdir()` opens the directory if necessary, loops `FBT_READDIR` requests bounded by `max_read`, validates returned `dirent` records and names, and copies them to the user `uio`.
- `fusefs_readlink()` requests symlink text, rejects embedded NULs, and copies to caller.
- `fusefs_read()` and `fusefs_write()` chunk I/O by `max_read`, use selected FUSE handles, update file size/UVM state after writes, and uncache stale pages.
- `fusefs_inactive()` releases all open FUSE handles without propagating errors; `fusefs_reclaim()` releases any still-valid handles, asks daemon to reclaim non-root nodes, removes inode hash entries, and frees node memory.
- `fusefs_lock()`, `fusefs_unlock()`, and `fusefs_islocked()` use per-node recursive rwlocks; `fusefs_advlock()` delegates to `lf_advlock()`; `fusefs_fsync()` sends optional `FBT_FSYNC` for writable handles.

Filesystem relevance:
- This file is the concrete vnode implementation for OpenBSD FUSE and encodes most daemon-facing filesystem semantics.
- It also documents protocol impedance mismatches, especially lack of true per-file-descriptor handle visibility in OpenBSD VFS.
