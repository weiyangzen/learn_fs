# File Research: sources/os/bsd/netbsd-src/lib/libc/tls/Makefile.inc

## Purpose
Adds libc TLS support sources to the NetBSD libc build.

## Build Behavior
Includes `bsd.own.mk`, extends `.PATH` with the local directory and `${ARCHDIR}/tls`, adds `tls.c` to `SRCS`, and compiles it with `_LIBC_SOURCE` and GNU11 mode.

## Dependencies
Relies on the parent libc make infrastructure for `${.PARSEDIR}`, `${ARCHDIR}`, and per-file `CPPFLAGS`.

## Risks And Notes
This file is purely build glue. Architecture-specific TLS support is found through `${ARCHDIR}/tls`; this include only guarantees the generic `tls.c` is compiled with libc-private settings.
