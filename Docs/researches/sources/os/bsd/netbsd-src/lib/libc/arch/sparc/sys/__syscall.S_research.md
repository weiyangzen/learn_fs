# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__syscall.S

## Summary
Provides SPARC `__syscall`.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
Used for raw system calls that need the `__syscall` entry point.
