# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/pipe.S

## Summary
Implements x86_64 `_pipe()` with weak `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned descriptors from `%eax` and `%edx` into the user array.
- Returns zero on success.

## Notes
Descriptor storage uses 32-bit writes.
