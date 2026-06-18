# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/preadv.c

## Purpose
Implements `preadv` with historical 64-bit offset padding.

## Key Elements
Calls `__preadv(fd, iovp, iovcnt, 0, offset)`.

## Dependencies
Uses `<sys/uio.h>`, syscall headers, and internal `__preadv`.

## Behavior/Risks
No local validation; vector and offset behavior are delegated to the syscall.
