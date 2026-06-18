# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/Makefile

This kernel include makefile installs ext2fs public headers under `/usr/include/ufs/ext2fs`.

Installed headers:
- `ext2fs.h`
- `ext2fs_dinode.h`
- `ext2fs_dir.h`
- `ext2fs_extents.h`
- `ext2fs_extern.h`

It sets `INCSDIR` and includes NetBSD’s `bsd.kinc.mk`.
