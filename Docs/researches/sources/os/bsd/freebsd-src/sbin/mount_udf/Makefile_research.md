# File Research: sources/os/bsd/freebsd-src/sbin/mount_udf/Makefile

## Summary
Builds the `mount_udf` runtime helper.

## Main Elements
- Builds `PROG=mount_udf`.
- Links `libkiconv` and `libutil`.
- Leaves dynamic linking enabled for optional userland libiconv access.
- Includes `bsd.prog.mk`.
