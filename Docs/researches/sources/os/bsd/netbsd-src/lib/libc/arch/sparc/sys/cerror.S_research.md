# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/cerror.S

## Summary
Implements SPARC libc syscall error handling.

## Key Details
- Reentrant builds call `__errno()` and store the error into thread-local errno.
- Non-reentrant builds store the error into global `errno`.
- Returns `-1` in `%o0` and `%o1`.
- Handles PIC and non-PIC global access.

## Notes
SPARC syscall macros branch here through the `ERROR()` macro.
