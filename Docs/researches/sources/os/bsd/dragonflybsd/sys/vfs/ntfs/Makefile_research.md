# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/Makefile

This kernel module Makefile builds the `ntfs` module from `ntfs_vfsops.c`, `ntfs_vnops.c`, `ntfs_subr.c`, `ntfs_ihash.c`, and `ntfs_compr.c`. It also includes generated/config header `opt_ntfs.h`.

The Makefile declares `SUBDIR= ntfs_iconv`, so the optional NTFS iconv helper module is built as a subdirectory module.

Research notes: module composition makes `ntfs_subr.c` the core metadata/data-path helper, `ntfs_vfsops.c` the mount/VFS layer, `ntfs_vnops.c` the vnode interface, `ntfs_ihash.c` the in-core inode hash, and `ntfs_compr.c` compressed attribute support.
