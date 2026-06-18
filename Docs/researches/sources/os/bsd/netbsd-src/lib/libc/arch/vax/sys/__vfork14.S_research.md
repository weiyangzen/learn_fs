# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__vfork14.S

## Summary
Implements VAX `__vfork14()`.

## Key Details
- Saves the caller return address before altering the stack frame.
- Returns out of the current frame before issuing the `vfork` trap.
- Calls `SYS___vfork14`.
- Returns zero in child and pid in parent.
- Handles errors inline, with reentrant and non-reentrant errno paths.

## Notes
The stack-return trick is required because parent and child cannot both safely `ret` from the same VAX frame after `vfork`.
