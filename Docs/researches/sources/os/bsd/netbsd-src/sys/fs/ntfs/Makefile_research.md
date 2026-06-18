# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/Makefile

Kernel include installation makefile for NTFS public headers.

Key contents:
- Installs headers under `/usr/include/ntfs`.
- Installs `ntfs.h`, `ntfs_inode.h`, and `ntfsmount.h`.
- Includes NetBSD `bsd.kinc.mk`.

Role:
- This is not the filesystem build file; it controls exported kernel/user-visible include installation.
