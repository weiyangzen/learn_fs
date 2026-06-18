# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_mount.h

This header defines the userspace-to-kernel mount argument ABI for TMPFS.

`TMPFS_ARGS_VERSION` is version 2. `struct tmpfs_mount_info` carries requested node limit, filesystem size limit, maximum file size, and root uid/gid/mode. The `MNT_*` flag constants identify which mount parameters were supplied: gid, uid, mode, inodes, size, and max file size.

The kernel VFS mount implementation consumes this structure in `tmpfs_vfsops.c`.
