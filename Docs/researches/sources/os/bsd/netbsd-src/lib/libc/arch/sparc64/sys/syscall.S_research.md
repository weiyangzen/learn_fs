# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/syscall.S

## Summary
Provides SPARC64 `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Relies on `SYS.h` for weak alias, trap, and error handling.

## Notes
This is the raw syscall dispatch entry for SPARC64 libc.
