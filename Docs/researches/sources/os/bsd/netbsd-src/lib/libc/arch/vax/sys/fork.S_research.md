# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/fork.S

## Summary
Implements VAX `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Tests `%r1` to distinguish parent from child.
- Clears `%r0` in the child.
- Returns pid in parent, zero in child.

## Notes
The kernel places the parent/child flag in `%r1`.
