# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__clone.S

## Summary
Implements SPARC `__clone()` and weak `clone` alias.

## Key Details
- Validates non-null function and stack arguments.
- Allocates a caller frame on the child stack and stores function and argument there.
- Calls `SYS___clone` with `(flags, stack)`.
- Parent returns the syscall result.
- Child retrieves the saved function and argument, calls it, then exits via `_exit`.
- Invalid inputs return `EINVAL` through `cerror`.

## Notes
The frame allocation is required by the SPARC register-window ABI.
