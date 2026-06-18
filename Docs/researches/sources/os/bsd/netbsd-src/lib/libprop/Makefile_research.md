# File Research: sources/os/bsd/netbsd-src/lib/libprop/Makefile

## Purpose
Builds NetBSD `libprop`, the property container/object library.

## Main Responsibilities
- Includes shared source definitions from `common/lib/libprop/Makefile.inc`.
- Builds with `_LIBPROP`, `_REENTRANT`, libc-private includes, hidden symbol visibility, and shared library installation.
- Defines `LIB=prop`.
- Installs manuals and many MLINK aliases for arrays, dictionaries, bools, data, numbers, strings, object iteration, externalization/internalization, utility getters/setters, ioctl/syscall send/recv helpers, and ingest APIs.

## Dependencies
- Common `libprop` source tree.
- `bsd.lib.mk`.
