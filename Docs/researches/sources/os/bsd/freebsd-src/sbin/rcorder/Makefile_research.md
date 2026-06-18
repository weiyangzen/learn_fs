# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/Makefile

Build file for `rcorder`.

Key elements:
- Builds `rcorder` from `ealloc.c`, `hash.c`, and `rcorder.c`.
- Links `libutil`.
- Defines `ORDER` in `CFLAGS`, enabling `Hash_GetKey` support.
- Installs `rcorder.8`.

Dependencies:
- Uses `bsd.prog.mk`.
