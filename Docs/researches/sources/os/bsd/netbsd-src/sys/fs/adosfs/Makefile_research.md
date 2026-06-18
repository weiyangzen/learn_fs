# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/Makefile

## Summary
Installs public ADOSFS headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/adosfs`.
- Installs `adosfs.h`.
- Includes `bsd.kinc.mk`.

## Integration Notes
The implementation sources are kernel build inputs elsewhere; this Makefile is for header installation.
