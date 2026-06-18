# File Research: sources/os/bsd/netbsd-src/sys/ufs/Makefile

Read completely: 7 lines.

Kernel include makefile for the UFS-related subtree. It lists `ffs`, `lfs`, `mfs`, `ufs`, and `ext2fs` as subdirectories, sets `INCSDIR` to `/usr/include/ufs`, and includes `<bsd.kinc.mk>`.

Risks and notes:
- This is build-system metadata; changing `SUBDIR` or `INCSDIR` affects which UFS-family headers are installed.
