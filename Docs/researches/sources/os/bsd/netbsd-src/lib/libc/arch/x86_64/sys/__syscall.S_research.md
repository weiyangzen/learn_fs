# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__syscall.S

## Summary
Provides x86_64 `__syscall`.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
Raw trap behavior is defined in the x86_64 syscall macro layer.
