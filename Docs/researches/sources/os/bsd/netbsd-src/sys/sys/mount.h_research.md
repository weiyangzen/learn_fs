# File Research: sources/os/bsd/netbsd-src/sys/sys/mount.h

## Purpose
Defines NetBSD VFS mount ABI and kernel mount infrastructure: filesystem type names, `struct mount`, `struct vfsops`, WAPBL hook dispatch, legacy export argument layouts, VFS kernel entry points, and userland mount-related declarations.

## Main API
- Public constants: `MNAMELEN`, `MOUNT_*` filesystem type strings, `VFS_*` sysctl identifiers, `VQ_MOUNT`, `VQ_UNMOUNT`.
- Kernel structures: `struct mount`, `struct vfsops`, `struct wapbl_ops`, `struct vfs_hooks`.
- VFS operation wrappers: `VFS_MOUNT`, `VFS_START`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_SYNC`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_SNAPSHOT`, `VFS_EXTATTRCTL`, `VFS_SUSPENDCTL`.
- Filesystem implementation helper macro: `VFS_PROTOS(fsname)`.
- Kernel mount lifecycle and lookup helpers: `vfs_getvfs`, `vfs_mountroot`, `vfs_busy`, `vfs_unbusy`, `vfs_attach`, `vfs_detach`, `vfs_ref`, `vfs_rele`, `vfs_mountalloc`, `dounmount`, `do_sys_mount`.
- Quota forwarding helpers: `vfs_quotactl_*`.
- Userland declarations: `getfh`, `unmount`, `mount`, `fhopen`, `fhstat`.

## Dependencies
Pulls in core system headers including `sys/param.h`, `sys/ucred.h`, `sys/statvfs.h`, and, for kernel/exposed mount consumers, `sys/uio.h`, `sys/queue.h`, `sys/rwlock.h`, `sys/specificdata.h`, and `sys/condvar.h`.

## Risks and Notes
This is a central ABI boundary. `struct export_args30` is explicitly frozen for old binary mount utilities. `struct mount` separates mostly stable and volatile data and aligns `mnt_refcnt` to avoid cache contention. WAPBL hooks are indirection shims for journaling support and require valid `mnt_wapbl_op` before macro use.
