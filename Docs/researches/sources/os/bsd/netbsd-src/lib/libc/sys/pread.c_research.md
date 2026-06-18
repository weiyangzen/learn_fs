# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pread.c

## Purpose
Implements `_sys_pread` with historical 64-bit offset padding.

## Key Elements
Weak-aliases `pread` and `_pread` to `_sys_pread`; calls `__pread(fd, buf, nbyte, 0, offset)`.

## Dependencies
Uses syscall headers, `<unistd.h>`, and internal `__pread`.

## Behavior/Risks
Preserves weak symbol layout for libc/syscall interposition while matching the padded syscall ABI.
