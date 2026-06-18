# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/cerror.S

## Summary
Implements SH3 libc syscall error handling.

## Key Details
- Stores the syscall error number into thread-local `__errno()` for `_REENTRANT` builds.
- Stores into global `errno` for non-reentrant builds.
- Returns `-1` in both `r0` and `r1`.
- Supports PIC and non-PIC global access.

## Notes
All SH3 syscall wrappers that use `JUMP_CERROR` depend on this return convention.
