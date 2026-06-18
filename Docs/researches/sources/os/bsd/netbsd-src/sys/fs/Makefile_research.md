# File Research: sources/os/bsd/netbsd-src/sys/fs/Makefile

## Summary
Kernel include build dispatcher for NetBSD filesystem public headers.

## Main Responsibilities
- Lists filesystem subdirectories including `adosfs`, `autofs`, `cd9660`, and many others.
- Includes `bsd.kinc.mk`.

## Integration Notes
This controls which filesystem header directories participate in kernel/user include installation.
