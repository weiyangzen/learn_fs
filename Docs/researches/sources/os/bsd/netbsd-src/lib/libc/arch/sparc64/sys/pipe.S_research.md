# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/pipe.S

## Summary
Implements SPARC64 `_pipe()` with weak `pipe` alias.

## Key Details
- Saves pointer to the user descriptor array.
- Calls `SYS_pipe`.
- Stores descriptors from `%o0` and `%o1`.
- Returns zero on success.

## Notes
The descriptor array stores 32-bit ints even on the 64-bit ABI.
