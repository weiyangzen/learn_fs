# File Research: sources/local-fs/jfsutils/mkfs/Makefile

Configured Automake-generated makefile for building `jfs_mkfs` in this checked-out tree.

Key build details:
- Builds `jfs_mkfs$(EXEEXT)` from `initmap.c`, `inodemap.c`, `inodes.c`, `mkfs.c`, and headers.
- Links `../libfs/libfs.a -luuid`.
- Adds `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- Installs the binary into `/sbin`.
- Installs `jfs_mkfs.8` and creates compatibility hard links:
  - `/sbin/mkfs.jfs` -> `jfs_mkfs`
  - `mkfs.jfs.8` -> `jfs_mkfs.8`
- Includes concrete configure outputs: `CC=gcc`, `CFLAGS=-g -O2`, `AM_CFLAGS=-Wall -Wstrict-prototypes -fno-strict-aliasing`, `host_alias=mipsel-buildroot-linux-uclibc-`, and `/data2/jfsutils-1.1.15` build paths.

Filesystem relevance: configured build metadata for the JFS formatter.
