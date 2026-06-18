# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/Makefile

This kernel include Makefile installs public SysV BFS headers:

- `INCSDIR= /usr/include/fs/sysvbfs`
- `INCS= bfs.h sysvbfs_args.h`
- includes `<bsd.kinc.mk>`

Its purpose is export/install metadata. In this group, `bfs.h` is the relevant on-disk/core API header; `sysvbfs_args.h` is referenced for installation but not part of this file list. There is no runtime logic in the Makefile.
