# File Research: sources/os/bsd/freebsd-src/sbin/mount_nullfs/Makefile

## Summary
Builds the `mount_nullfs` runtime helper.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mount_nullfs`.
- Links `libutil`.
- Includes `bsd.prog.mk`.
