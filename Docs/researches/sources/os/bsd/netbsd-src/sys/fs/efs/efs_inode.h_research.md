# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_inode.h

Read completely: 73 lines.

Defines the in-core EFS inode. `struct efs_inode` embeds a genfs node, advisory lock pointer, inode identity/device/vnode pointers, cached host-order metadata fields, and a verbatim copy of the on-disc `efs_dinode`.

The cached fields mirror the disk inode with NetBSD-native types and byte order: mode, nlink, uid, gid, size, times, generation, extent count, and version. Conversion is performed by helpers in `efs_subr.c`.

Also defines `EFS_VTOI()`/`EFS_ITOV()` and the NFS file-handle payload `struct efs_fid`, which carries inode number and generation after the standard `fid` prefix.
