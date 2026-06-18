# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vfsops.c

Read completely: 147 lines.

Implements generic UFS VFS helper operations shared by FFS/MFS-style filesystems.

Core behavior:
- `ufs_start()` is currently a no-op.
- `ufs_root()` fetches `ROOTINO` via `VFS_VGET()`.
- `ufs_check_export()` looks up network export credentials and returns export flags and anonymous credential.
- `ufs_init()` runs once, initializing inode hash, quota subsystem, and optional dirhash subsystem.
- `ufs_fhtovp()` converts UFS file handles to vnodes through `VFS_VGET()`, then validates mode and generation number before returning the vnode.

Integration and risks:
- `ufs_init()` is shared initialization and must be idempotent.
- File-handle validation depends on stable inode generation numbers to reject stale NFS handles.
- Export support is mount-specific through `ufsmount.um_export`.
