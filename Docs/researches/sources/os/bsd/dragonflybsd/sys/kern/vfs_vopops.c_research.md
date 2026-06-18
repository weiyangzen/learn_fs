# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vopops.c

Read completely: 2227 lines.

This file implements the vnode operation wrapper layer. All DragonFlyBSD VOP calls pass through these wrappers, which construct argument objects, select vnode operation descriptors, acquire legacy MP locks when needed, and dispatch into filesystem-specific operation tables.

Key responsibilities:
- Defines `syslink_desc` descriptors for every vnode op through `VNODEOP_DESC_INIT`.
- Wraps old path-based operations: lookup, create, whiteout, mknod, remove, link, rename, mkdir, rmdir, and symlink.
- Wraps primary vnode operations: open, close, access, getattr, setattr, read, write, ioctl, poll, kqfilter, mmap, fsync, fdatasync, readdir, readlink, inactive, reclaim, bmap, strategy, pathconf, advlock, balloc, pages, ACLs, extended attributes, mountctl, markatime, and allocate.
- Wraps the newer namecache API: nresolve, nlookupdotdot, ncreate, nmkdir, nmknod, nlink, nsymlink, nwhiteout, nremove, nrmdir, and nrename.
- Provides forwarding helpers for passthrough filesystems, cache-coherency dispatch, and journaling dispatch.
- Provides `_ap` forms that dispatch an already-built argument structure.

Important behavior:
- Most wrappers use `VFS_MPLOCK()` or `VFS_MPLOCK_FLAG()` to acquire the giant MP lock only for non-MPSAFE mounts or operation classes.
- `vop_open()` ages vnodes back toward active use by clearing/decrementing `VAGE*` flags.
- `vop_write()` performs quota pre-checks for regular files, estimates append growth, and updates VFS space accounting after success.
- `vop_nremove()` records attributes before deletion and subtracts file size from accounting when the removed object had one hard link.
- `vop_strategy()` has a special no-mount fallback for swap.

Security/reliability notes:
- This is a central ABI/locking boundary between generic VFS code and filesystem implementations.
- Quota/accounting estimates in `vop_write()` are based on pre-write size and requested length; unusual filesystem write semantics can make accounting approximate.
- Reclaim/inactive wrappers explicitly account for operations that can clear `vp->v_mount`.
