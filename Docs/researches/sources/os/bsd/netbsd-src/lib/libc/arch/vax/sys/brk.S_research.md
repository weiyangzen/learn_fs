# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/brk.S

## Summary
Implements VAX `_brk()` with weak `brk` alias.

## Key Details
- Uses hidden `__minbrk` and `__curbrk`.
- Clamps requested break below `__minbrk`.
- Calls `SYS_break`.
- Updates `__curbrk` and returns zero on success.
- Jumps to `CERROR+2` on failure.

## Notes
The current and minimum break symbols are hidden libc internals.
