# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs.h

This is the primary SMBFS mount-interface header. It defines the SMBFS VFS type/version constants, mount flags, max path component count, and the userspace/kernel mount argument structure `struct smbfs_args`.

`struct smbfs_args` carries the mount protocol version, netsmb device handle, mount flags, mount/root paths, uid/gid ownership mapping, file and directory modes, and case-conversion option. These fields drive both VFS presentation and SMB name conversion behavior.

Under `_KERNEL`, the file defines `struct smbmount`, the per-mount control block. It links the DragonFly mount to the SMB share, root smbnode, owner/mount credentials, case options, vnode-name lookup stack, and smbnode hash table protected by `sm_hashlock`. It also exposes conversion macros such as `VFSTOSMBFS`, `VTOSMBFS`, and `VTOVFS`.

The exported prototypes connect this header to I/O and vnode code: `smbfs_ioctl`, `smbfs_doio`, and `smbfs_vinvalbuf`.
