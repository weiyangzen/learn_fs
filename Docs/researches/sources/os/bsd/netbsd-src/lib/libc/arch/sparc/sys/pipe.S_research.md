# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/pipe.S

## Summary
Implements SPARC `_pipe()` with weak `pipe` alias.

## Key Details
- Saves the user file-descriptor array pointer.
- Calls `SYS_pipe`.
- Stores returned descriptors from `%o0` and `%o1`.
- Returns zero on success.

## Notes
Errors dispatch to the shared `ERROR()` path.
