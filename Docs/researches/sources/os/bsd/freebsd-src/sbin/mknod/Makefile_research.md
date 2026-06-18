# File Research: sources/os/bsd/freebsd-src/sbin/mknod/Makefile

## Summary
Builds the `mknod` runtime utility and its manual page.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mknod`.
- Installs `mknod.8`.
- Includes `bsd.prog.mk`.
