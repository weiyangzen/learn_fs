# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/syscall.S

## Summary
Provides SH3 `syscall()` and internal `_syscall` wrapper.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- The weak/public alias behavior is defined by `SYS.h`.

## Notes
This is the generic raw syscall interface for callers supplying a syscall number.
