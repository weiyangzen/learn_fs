# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/fork.S

## Summary
Implements SH3 `__fork()`.

## Key Details
- Invokes `SYS_fork`.
- Uses `r1` to distinguish parent from child.
- Returns zero in the child and the child pid in the parent.
- Dispatches to `cerror` on failure.

## Notes
The function directly uses `trapa #0x80` rather than the generic macro wrapper.
