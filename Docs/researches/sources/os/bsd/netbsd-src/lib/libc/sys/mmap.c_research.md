# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/mmap.c

## Purpose
Implements `mmap` as a padded call to the internal syscall entry.

## Key Elements
Weak-aliases `mmap` to `_mmap` and calls `__mmap(addr, len, prot, flags, fd, 0, offset)`.

## Dependencies
Uses `<sys/mman.h>`, syscall headers, and internal `__mmap`.

## Behavior/Risks
The wrapper preserves the historical 64-bit offset padding ABI; all mapping semantics live in the kernel syscall.
