# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/pipe.S

## Summary
Implements SH3 `_pipe()` with weak public `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned file descriptors from `r0` and `r1` into the caller-provided array.
- Returns zero on success.

## Notes
Error handling is inherited from `_SYSCALL`.
