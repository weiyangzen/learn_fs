# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pwrite.c

## Purpose
Implements `_sys_pwrite` with historical 64-bit offset padding.

## Key Elements
Weak-aliases `pwrite` and `_pwrite` to `_sys_pwrite`; calls `__pwrite(fd, buf, nbyte, 0, offset)`.

## Dependencies
Uses syscall headers, `<unistd.h>`, and internal `__pwrite`.

## Behavior/Risks
Maintains both public and internal symbol compatibility around the padded syscall.
