# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/brk.S

## Summary
Implements SPARC64 `_brk()` with weak `brk` alias.

## Key Details
- Defines 64-bit `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk`.
- Calls `SYS_break`.
- Updates `__curbrk` on success and returns zero.
- Provides code paths for PIC level 2, PIC level 1, and non-PIC.

## Notes
Uses 64-bit loads/stores and SPARC64 conditional moves.
