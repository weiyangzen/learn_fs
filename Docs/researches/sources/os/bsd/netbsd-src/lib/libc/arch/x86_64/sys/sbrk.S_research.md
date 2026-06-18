# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/sbrk.S

## Summary
Implements x86_64 `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines `CURBRK` initialized to `_end`.
- Returns current break immediately for zero increment.
- For nonzero increment, computes new break and calls `SYS_break`.
- Returns old break and updates `CURBRK` on success.
- Provides PIC and non-PIC code paths.

## Notes
The non-PIC path saves the increment in `%rsi` to update `CURBRK` after the syscall.
