# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/Makefile

This short makefile installs public FFS kernel headers.

Contents:
- Sets `INCSDIR= /usr/include/ufs/ffs`.
- Installs `ffs_extern.h` and `fs.h`.
- Includes `<bsd.kinc.mk>`.

Role:
- This is part of the kernel include installation machinery, not runtime filesystem logic.
