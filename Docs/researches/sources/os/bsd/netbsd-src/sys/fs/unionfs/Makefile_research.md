# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/Makefile

Read completely: 7 lines.

Installs the newer `unionfs` public kernel header into the same historical include directory as the legacy union filesystem.

It sets `INCSDIR` to `/usr/include/miscfs/union`, installs `union.h`, and includes `bsd.kinc.mk`. In this source tree the installed file is `unionfs/unionfs.h`, but the public installed name is still `union.h`.
