# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/sbrk.S

## Summary
Implements SH3 `_sbrk()` with weak public `sbrk` alias.

## Key Details
- Defines `curbrk` initialized to `_end`.
- Computes the requested new break as `curbrk + increment`.
- Calls `SYS_break`.
- On success, returns the old break and updates `curbrk`.
- Supports PIC and non-PIC addressing.

## Notes
The code does not special-case zero increments; it still goes through the break syscall.
