# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.h

Read completely: 26 lines.

Declares the EFS genfs integration points: external `efs_genfsops` and `efs_gop_alloc()`.

This small header lets the VFS/vnode loading path initialize EFS vnodes with the filesystem’s genfs operations table.
