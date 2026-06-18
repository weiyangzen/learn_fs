# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/syscall.S

## Summary
Provides x86_64 `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Relies on `SYS.h` for aliasing, trap setup, and error handling.

## Notes
This is the public raw syscall entry point.
