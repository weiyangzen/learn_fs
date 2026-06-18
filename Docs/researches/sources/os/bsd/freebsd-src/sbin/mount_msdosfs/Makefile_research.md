# File Research: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/Makefile

## Summary
Builds the `mount_msdosfs` runtime helper.

## Main Elements
- Builds `PROG=mount_msdosfs`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
