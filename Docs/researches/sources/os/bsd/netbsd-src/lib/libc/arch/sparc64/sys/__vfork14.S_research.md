# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__vfork14.S

## Summary
Implements SPARC64 `__vfork14()`.

## Key Details
- Uses `SYSCALL(__vfork14)`.
- Converts `%o1` parent/child flag into a return mask.
- Returns zero in the child and child pid in the parent.

## Notes
Matches SPARC-family fork return handling.
