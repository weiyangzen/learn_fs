# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ftruncate.c

## Purpose
Implements `ftruncate` as a padded call to the internal syscall entry.

## Key Elements
Defines weak alias `ftruncate` to `_ftruncate` when supported and calls `__ftruncate(fd, 0, length)`.

## Dependencies
Uses libc namespace headers, syscall headers, and internal `__ftruncate`.

## Behavior/Risks
Maintains compatibility with historical GCC 1.x 64-bit offset argument padding.
