# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/fdiscard.c

## Purpose
Provides `fdiscard` compatibility glue for the kernel syscall ABI.

## Key Elements
Calls `__fdiscard(fd, 0, off, len)` to supply historical 64-bit offset padding.

## Dependencies
Uses `<sys/types.h>`, `<sys/syscall.h>`, and `<unistd.h>`.

## Behavior/Risks
The wrapper's only behavior is ABI padding; wrong padding would break old syscall argument layout on affected compilers/architectures.
