# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/fork.S

## Summary
Implements SPARC `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%o1` to form a parent/child mask.
- Returns zero in child, pid in parent.

## Notes
The parent/child return convention is the same as `__vfork14.S`.
