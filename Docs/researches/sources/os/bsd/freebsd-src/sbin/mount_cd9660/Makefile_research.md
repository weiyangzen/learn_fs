# File Research: sources/os/bsd/freebsd-src/sbin/mount_cd9660/Makefile

## Summary
Builds the `mount_cd9660` runtime helper.

## Main Elements
- Builds `PROG=mount_cd9660`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
