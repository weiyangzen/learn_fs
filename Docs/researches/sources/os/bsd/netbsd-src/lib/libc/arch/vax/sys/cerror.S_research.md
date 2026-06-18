# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/cerror.S

## Summary
Implements VAX syscall error handling.

## Key Details
- Entry symbol is `__cerror`.
- Reentrant builds call `__errno()` and store the saved error.
- Non-reentrant builds store into global `errno`.
- Returns `-1` in `%r0` and `%r1`.

## Notes
Many VAX wrappers jump to `CERROR+2`, entering after the no-op prefix expected by `SYS.h`.
