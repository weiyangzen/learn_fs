# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/shmat.S

## Summary
Provides SH3 `shmat()` as a regular syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
No local ABI adjustment is needed.
