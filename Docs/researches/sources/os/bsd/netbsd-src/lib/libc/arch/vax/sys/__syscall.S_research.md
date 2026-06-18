# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__syscall.S

## Summary
Implements VAX `__syscall()`.

## Key Details
- Loads syscall number from the first argument.
- Adjusts `%ap` to skip the first two argument-list entries used by `__syscall`.
- Reduces the VAX argument count by two.
- Executes `chmk` with the requested syscall number.
- Returns on success or jumps to `CERROR+2` on carry set.

## Notes
This differs from `syscall.S`, which skips only one argument.
