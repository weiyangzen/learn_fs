# File Research: sources/os/bsd/openbsd-src/sbin/growfs/Makefile

## Scope

Build file for OpenBSD `growfs`.

## Build Role

- Builds `PROG=growfs` with manual page `growfs.8`.
- Links `libutil`.
- Contains commented `CFLAGS+=-Wall`.

## Dependencies

The source is standalone `growfs.c` plus OpenBSD system headers and `libutil` device helpers.
