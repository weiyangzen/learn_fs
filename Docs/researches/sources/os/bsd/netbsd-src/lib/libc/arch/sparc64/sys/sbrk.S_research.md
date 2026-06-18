# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/sbrk.S

## Summary
Implements SPARC64 `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines 64-bit `__curbrk` initialized to `_end`.
- Computes new break from old break plus increment.
- Calls `SYS_break`.
- Returns old break and updates `__curbrk` on success.
- Supports PIC level 2, PIC level 1, and non-PIC modes.

## Notes
All break bookkeeping is 64-bit.
