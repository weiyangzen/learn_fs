# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/brk.S

## Summary
Implements SPARC `_brk()` with weak `brk` alias.

## Key Details
- Defines `__minbrk` initialized to `_end`.
- Clamps requests below the minimum break.
- Calls `SYS_break`.
- On success, updates `CURBRK` and returns zero.
- Contains PIC and non-PIC code paths.

## Notes
The stored current break symbol comes from `SYS.h` as `CURBRK`.
