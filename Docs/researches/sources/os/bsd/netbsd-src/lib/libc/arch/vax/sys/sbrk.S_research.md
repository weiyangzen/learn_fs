# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/sbrk.S

## Summary
Implements VAX `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines hidden `__minbrk` and `__curbrk` initialized to `_end`.
- Constructs a temporary argument list for `SYS_break`.
- Calls `break` with `__curbrk + increment`.
- Returns the old break and updates `__curbrk` on success.
- Jumps to `CERROR+2` on failure.

## Notes
The wrapper manually rewrites `%ap` to call the kernel with the synthetic argument list.
