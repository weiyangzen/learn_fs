# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/pipe.S

## Summary
Implements VAX `_pipe()` with weak `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned descriptors from `%r0` and `%r1` into the caller array.
- Returns zero on success.

## Notes
The descriptor pointer is the first user argument.
