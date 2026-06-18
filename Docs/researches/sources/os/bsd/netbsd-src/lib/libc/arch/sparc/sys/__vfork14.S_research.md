# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__vfork14.S

## Summary
Implements SPARC `__vfork14()`.

## Key Details
- Uses `SYSCALL(__vfork14)`.
- Converts the kernel's parent/child flag in `%o1` into a return mask.
- Returns zero in the child and child pid in the parent.

## Notes
This mirrors the SPARC `fork` return-value convention.
