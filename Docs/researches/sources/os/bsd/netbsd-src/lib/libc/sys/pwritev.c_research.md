# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pwritev.c

## Purpose
Implements `pwritev` with historical 64-bit offset padding.

## Key Elements
Calls `__pwritev(fd, iovp, iovcnt, 0, offset)`.

## Dependencies
Uses `<sys/uio.h>`, syscall headers, and internal `__pwritev`.

## Behavior/Risks
Thin ABI shim; write-vector validation and partial-write behavior are syscall responsibilities.
