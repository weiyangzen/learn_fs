# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/ptrace.S

## Summary
Implements x86_64 `ptrace()`.

## Key Details
- Saves all four syscall arguments.
- Calls `__errno()` before the syscall.
- Restores arguments and invokes `SYS_ptrace`.
- Dispatches to `__cerror` on carry-set failure.

## Notes
Although the comment says errno is set to zero, the code only calls `__errno()` and restores arguments; it does not visibly store zero in the shown assembly.
