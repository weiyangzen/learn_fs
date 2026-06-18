# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/mknodat.c

## Purpose
Provides `mknodat` ABI glue.

## Key Elements
Calls `__mknodat(fd, path, mode, 0, dev)` to include the internal padding argument.

## Dependencies
Uses `<sys/stat.h>` and syscall declarations.

## Behavior/Risks
No validation locally; all path, mode, and device handling is delegated to the syscall.
