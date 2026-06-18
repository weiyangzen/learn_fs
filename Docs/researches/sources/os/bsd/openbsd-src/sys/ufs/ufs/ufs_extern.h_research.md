# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_extern.h

Read completely: 132 lines.

Declares exported UFS vnode, VFS, inode-cache, inode-lifecycle, lookup, bmap, quota-adjacent, special-device, FIFO, and helper functions.

Core definitions:
- Lists vnode operation entry points for access, create, mknod, open/close, attributes, directory operations, symlink/readlink, strategy, locking, pathconf, advisory locks, kqueue filter, and special/FIFO wrappers.
- Declares block mapping helpers `ufs_bmaparray()` and `ufs_getlbns()`.
- Declares inode hash lifecycle: initialization, lookup, insert, and remove.
- Declares generic inactive/reclaim and directory manipulation helpers.
- Declares generic VFS hooks such as start, root, quotactl, file-handle conversion, and export checks.
- Declares `ufs_itimes()` and `ufs_makeinode()` used by filesystem-specific vnode implementations.

Integration and risks:
- This header is the cross-module contract tying FFS, MFS, ext2-adjacent code, and generic UFS routines together.
- Signature drift here would break vnode/VFS operation vectors.
