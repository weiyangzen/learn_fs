# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/Makefile

This kernel include makefile installs public MFS headers.

Key contents:
- Sets `INCSDIR` to `/usr/include/ufs/mfs`.
- Installs `mfs_extern.h` and `mfsnode.h`.
- Includes `bsd.kinc.mk`.

Role:
- Build-system glue only; no runtime filesystem logic.
