# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__syscall.S

## Summary
Provides the SH3 `__syscall` raw syscall entry.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
All trap mechanics and error handling come from the SH3 syscall macro layer.
