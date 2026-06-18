# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/Makefile.inc

This OpenBSD make include adds `${.CURDIR}/libunbound/libunbound` to `.PATH` and appends `context.c`, `libunbound.c`, and `libworker.c` to `SRCS`.

It is the local build glue that brings the libunbound context/API/worker implementation into the `unwind`-vendored libunbound build.
