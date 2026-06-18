# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/Makefile

Kernel include installation makefile for ptyfs.

Key contents:
- Installs headers under `/usr/include/fs/ptyfs`.
- Installs `ptyfs.h`.
- Includes NetBSD `bsd.kinc.mk`.

Role:
- Controls export of the ptyfs mount/header interface.
