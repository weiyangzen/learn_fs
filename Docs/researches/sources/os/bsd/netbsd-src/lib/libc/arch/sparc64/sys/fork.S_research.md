# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/fork.S

## Summary
Implements SPARC64 `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%o1` to distinguish child from parent.
- Returns zero in child, pid in parent.

## Notes
The implementation is nearly identical to 32-bit SPARC with SPARC64 syntax.
