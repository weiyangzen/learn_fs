# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/Makefile

Source read: complete file, 8 lines.

Purpose: Kernel module makefile for the DragonFly HPFS filesystem implementation.

Key contents:
- Sets `KMOD= hpfs`.
- Builds `hpfs_vfsops.c`, `hpfs_vnops.c`, `hpfs_hash.c`, `hpfs_subr.c`, `hpfs_lookup.c`, and `hpfs_alsubr.c`.
- Includes `<bsd.kmod.mk>`.

Integration:
- Excludes headers from `SRCS`; they are consumed by the listed C files.
- The module registers VFS operations through `VFS_SET(hpfs_vfsops, hpfs, 0)` in `hpfs_vfsops.c`.

Risks and review notes:
- This makefile does not include optional iconv or helper modules; HPFS codepage conversion is internal to HPFS mount arguments and on-disk codepage tables.
