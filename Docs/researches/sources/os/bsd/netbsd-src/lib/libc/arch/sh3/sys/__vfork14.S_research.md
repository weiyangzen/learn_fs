# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__vfork14.S

## Summary
Implements SH3 `__vfork14()`.

## Key Details
- Invokes `SYS___vfork14` through `trapa #0x80`.
- Uses the second return register to distinguish parent from child.
- Returns child pid in the parent and zero in the child.
- Jumps to `cerror` on trap failure.

## Notes
The return-value adjustment mirrors SH3 `fork.S`.
