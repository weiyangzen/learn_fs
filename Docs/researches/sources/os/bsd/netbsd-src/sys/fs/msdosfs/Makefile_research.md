# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/Makefile

## Purpose
Installs public MSDOSFS/FAT filesystem headers.

## Main Contents
Sets `INCSDIR` to `/usr/include/msdosfs`, installs `bootsect.h`, `bpb.h`, `denode.h`, `direntry.h`, `fat.h`, and `msdosfsmount.h`, then includes `bsd.kinc.mk`.

## Dependencies
Part of NetBSD kernel include installation infrastructure.

## Risks and Notes
This file only manages header installation; implementation files are built elsewhere.
