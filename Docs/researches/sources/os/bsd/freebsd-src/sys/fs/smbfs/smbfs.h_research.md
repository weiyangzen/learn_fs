# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs.h

## Purpose

Defines public mount arguments, mount flags, version constants, and the kernel mount control block for FreeBSD SMBFS.

## Main Interface

Constants:
- `SMBFS_VERSION`, `SMBFS_VFSNAME`.
- mount flags such as soft, interruptible, strong, NLS present, and no-long-name mode.
- `SMBFS_MAXPATHCOMP`.

`struct smbfs_args` carries user mount parameters: device id, flags, mount point, root path, uid/gid, file/dir modes, and case option.

`struct smbmount` stores kernel mount state: owner uid/gid/modes, mount pointer, root node, device, owner credential, flags, next inode, share pointer, path stack, case option, and `sm_didrele` unmount/reclaim coordination flag.

Macros convert between mount, vnode, and smbfs mount objects.

Declared functions:
- `smbfs_ioctl()`
- `smbfs_doio()`
- `smbfs_vinvalbuf()`

## Integration Points

Included by SMBFS VFS, vnode, node, I/O, and SMB request implementation files. It ties SMBFS to `netsmb` share/device objects.

## Risks and Review Notes

This header represents SMBFS’s old SMB1-oriented mount state. Several fields, such as mount flags and root path buffers, are shared by user mount ABI and kernel internals, so compatibility constraints are high.
