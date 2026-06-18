# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_mount.h

Read completely: 40 lines.

Defines user mount arguments and the in-kernel EFS mount structure. `struct efs_args` carries the block-device path and a version field, with `EFS_MNT_VERSION` currently zero.

In kernel builds, `struct efs_mount` stores the in-core superblock copy, mounted device number, mount pointer, and block-device vnode pointer. This is the object reached through `VFSTOEFS(mp)`.
