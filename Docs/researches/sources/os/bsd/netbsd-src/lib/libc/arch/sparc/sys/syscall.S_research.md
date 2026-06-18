# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/syscall.S

## Summary
Provides SPARC `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Defers trap and error behavior to the macro definitions in `SYS.h`.

## Notes
This is the public raw syscall entry for SPARC libc.
