# File Research: sources/os/bsd/netbsd-src/lib/libc_aligned/Makefile

## Purpose
Builds `libc_aligned`, a support library containing libc routines that avoid unaligned memory access.

## Build Behavior
Selects an architecture include file from `arch/${LIBC_MACHINE_CPU}`, `arch/${MACHINE_ARCH}`, or `arch/${MACHINE}` if present, adds the matching path, and builds `LIB=c_aligned` only when `SRCS` is non-empty.

## Dependencies
Depends on NetBSD make variables, architecture-specific `Makefile.inc` files, and `bsd.lib.mk`.

## Risks And Notes
The library silently does not build if no matching architecture source list exists.
