# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/sbrk.S

## Summary
Implements SPARC `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines `CURBRK` initialized to `_end`.
- Computes new break as old break plus increment.
- Calls `SYS_break`.
- Returns the old break and updates `CURBRK` on success.
- Supports PIC and non-PIC addressing.

## Notes
Failure uses shared syscall error handling.
