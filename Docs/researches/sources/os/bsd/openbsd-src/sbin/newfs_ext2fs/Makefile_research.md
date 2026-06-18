# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/Makefile

Purpose: Builds OpenBSD `newfs_ext2fs`.

Build details:
- `PROG=newfs_ext2fs`.
- Sources are `newfs_ext2fs.c`, `mke2fs.c`, and `ext2fs_bswap.c`.
- Adds `.PATH` to `../../sys/ufs/ext2fs` for byte-swap support code.
- Links with `libutil`.
- Installs `newfs_ext2fs.8`.
- Uses standard `<bsd.prog.mk>`.
