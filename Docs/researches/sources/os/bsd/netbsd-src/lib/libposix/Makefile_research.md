# File Research: sources/os/bsd/netbsd-src/lib/libposix/Makefile

## Purpose
Builds the NetBSD `libposix` library, which supplies POSIX-specific replacement routines over libc behavior.

## Main Responsibilities
- Sets `LIB=posix`.
- Adds `_REENTRANT`, libc include, and kernel syscall include paths.
- Includes libc include setup and `sys/Makefile.inc`.
- Adds `_errno.c` from libc for `powerpc64`.
- Builds with standard `bsd.lib.mk`.

## Dependencies
- `bsd.own.mk`, libc include makefile fragments, `libposix/sys/Makefile.inc`.
