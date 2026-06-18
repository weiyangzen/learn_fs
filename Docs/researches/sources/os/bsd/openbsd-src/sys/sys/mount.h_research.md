# File Research: sources/os/bsd/openbsd-src/sys/sys/mount.h

Defines OpenBSD mount/statfs ABI, filesystem-specific mount argument structures, mount flags, VFS operation vectors, and kernel VFS entry points.

Key contents:
- Filesystem identity types: `fsid_t`, `fid`, `fhandle_t`.
- Export and mount args for UFS/MFS/ISO/NFS/MSDOS/NTFS/UDF/tmpfs/FUSE.
- NFS mount option flags and internal NFS state bits.
- `struct statfs` with counters, names, owner, timestamp, and `union mount_info`.
- Filesystem type names such as `ffs`, `nfs`, `mfs`, `msdos`, `cd9660`, `ext2fs`, `ntfs`, `udf`, `tmpfs`, `fuse`.
- Kernel `struct mount`, mount flags, visible flag mask, and busy flags.
- `struct vfsconf`, `struct bcachestats`, `struct vfsops`.

Key APIs:
- VFS operation macros: `VFS_MOUNT`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_STATFS`, `VFS_SYNC`, `VFS_VGET`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_CHECKEXP`.
- Kernel helpers: `vfs_busy`, `vfs_mount_alloc`, `vfs_mount_foreach_vnode`, `vfs_getvfs`, `vfs_export`, `vfs_syncwait`, `vfs_shutdown`, `dounmount`, `vfs_byname`.
- Userland declarations for `mount`, `unmount`, `statfs`, `fstatfs`, `getfsstat`, `getmntinfo`, and file-handle calls.

Risk notes:
- `statfs` and mount-argument layout are ABI surfaces.
- VFS operation tables and mount flags coordinate with vnode and filesystem implementations across the tree.
