# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/lseek.c

## Purpose
Implements `lseek` as a padded call to the internal syscall entry.

## Key Elements
Weak-aliases `lseek` to `_lseek` and calls `__lseek(fd, 0, offset, whence)`.

## Dependencies
Uses syscall headers, `<unistd.h>`, and internal `__lseek`.

## Behavior/Risks
Thin ABI shim; offset padding must match the kernel's syscall argument ABI.
