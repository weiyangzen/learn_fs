# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/Makefile

This Makefile builds the DragonFlyBSD `tmpfs` kernel module. It includes the four implementation files: `tmpfs_vnops.c`, `tmpfs_subr.c`, `tmpfs_fifoops.c`, and `tmpfs_vfsops.c`.

It declares no manual page with `NOMAN=` and delegates the actual module build rules to `bsd.kmod.mk`.
