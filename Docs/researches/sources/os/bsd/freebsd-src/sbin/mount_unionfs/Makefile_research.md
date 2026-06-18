# File Research: sources/os/bsd/freebsd-src/sbin/mount_unionfs/Makefile

## Summary
Builds the `mount_unionfs` runtime helper.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mount_unionfs`.
- Links `libutil`.
- Includes `bsd.prog.mk`.
