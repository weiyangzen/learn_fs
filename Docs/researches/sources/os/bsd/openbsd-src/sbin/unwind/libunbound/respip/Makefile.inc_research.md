# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/Makefile.inc

OpenBSD make fragment for the libunbound response-IP module.

Contents:
- Adds `${.CURDIR}/libunbound/respip` to `.PATH`.
- Adds `respip.c` to `SRCS`.

Role:
- Pulls response-IP support into the unwind/libunbound build.
