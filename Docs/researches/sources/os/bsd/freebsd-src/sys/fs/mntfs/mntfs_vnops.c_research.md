# File Research: sources/os/bsd/freebsd-src/sys/fs/mntfs/mntfs_vnops.c

Implements private `mntfs` character-device vnodes used by mounted filesystems to safely hold backing disk devices without depending directly on the application-visible devfs vnode.

Main responsibilities:
- Defines `mntfs_vnodeops`, using default vnode ops, standard fsync, panic strategy, and custom reclaim.
- `mntfs_allocvp()` allocates a private `VCHR` vnode associated with a mount and an existing device vnode’s `v_rdev`.
- `mntfs_freevp()` tears down the private vnode with `vgone()` and `vput()`.

Key implementation details:
- The design avoids devfs vnode invalidation problems when a device disappears. Filesystems can keep their own private vnode and clean dirty buffers in a controlled manner.
- `mntfs_allocvp()` requires the original vnode to be exclusively locked, takes a device reference with `dev_ref()`, unlocks the original vnode, locks the new vnode, and marks it constructed.
- `mntfs_reclaim()` releases the held device reference with `dev_rel()`.

Important dependencies:
- FreeBSD vnode lifecycle and device reference APIs: `getnewvnode`, `vn_lock`, `vn_set_state`, `vgone`, `vput`, `dev_ref`, `dev_rel`.
- Used by filesystems that need stable private access to their backing device vnode.

Notable risks and edge cases:
- `vop_strategy` is `VOP_PANIC`; the vnode is not intended for normal strategy I/O dispatch through this vector.
- Correct paired use of `mntfs_allocvp()` and `mntfs_freevp()` is required to balance device references.
