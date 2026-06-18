# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/fork.S

## Summary
Implements x86_64 `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%edx`, the kernel parent/child flag.
- Masks `%eax` so the child sees zero and the parent sees child pid.

## Notes
The file follows the common BSD fork dual-return convention.
