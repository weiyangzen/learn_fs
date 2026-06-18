# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/Makefile

## Purpose
Installs public HFS kernel headers.

## Main Contents
Sets `INCSDIR` to `/usr/include/fs/hfs`, installs `hfs.h` and `libhfs.h`, and includes `bsd.kinc.mk`.

## Dependencies
Part of NetBSD kernel include installation infrastructure.

## Risks and Notes
Only `hfs.h` and `libhfs.h` are exported; helper headers such as `unicode.h` remain internal to this subtree.
