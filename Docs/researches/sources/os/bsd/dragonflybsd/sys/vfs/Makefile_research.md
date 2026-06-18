# File Research: sources/os/bsd/dragonflybsd/sys/vfs/Makefile

## Summary
Top-level makefile for DragonFly BSD VFS modules.

## Main Responsibilities
- Lists VFS module subdirectories including fifofs, msdosfs, nfs, procfs, hpfs, ntfs, smbfs, isofs, mfs, udf, nullfs, hammer, tmpfs, autofs, ext2fs, fuse, and hammer2.
- Leaves `SUBDIR_ORDERED` empty to allow concurrent building.
- Includes `bsd.subdir.mk`.

## Risks
Build inclusion is controlled by this subdirectory list. Adding a VFS module elsewhere without updating this makefile can omit it from module builds.
