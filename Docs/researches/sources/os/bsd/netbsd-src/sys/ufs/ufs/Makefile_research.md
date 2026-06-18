# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/Makefile

This kernel include makefile installs public UFS headers.

Key contents:
- Sets `INCSDIR` to `/usr/include/ufs/ufs`.
- Installs disk-format, directory, extattr, inode, quota, byte-swap, extern, WAPBL, and mount headers.
- Includes `bsd.kinc.mk`.

Role:
- Build-system glue for exporting UFS kernel headers.
