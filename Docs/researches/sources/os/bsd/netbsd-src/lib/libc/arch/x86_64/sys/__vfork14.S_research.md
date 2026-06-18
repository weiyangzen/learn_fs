# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__vfork14.S

## Summary
Implements x86_64 `__vfork14()`.

## Key Details
- Pops the caller return address into `%r9` before syscall.
- Calls `SYS___vfork14`.
- Uses `%edx` parent/child flag to return zero in the child and pid in the parent.
- Jumps directly to saved return address on success.
- Restores the return address before dispatching to error handling on failure.

## Notes
Avoiding an ordinary return frame is important for vfork stack sharing.
