# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/shmat.S

## Summary
Provides x86_64 `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
Uses the standard x86_64 syscall macro path.
