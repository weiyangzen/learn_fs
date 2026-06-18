# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/cerror.S

## Summary
Implements x86_64 syscall error handling.

## Key Details
- Entry symbol is `__cerror`.
- Saves the error value in `%r12d` across the call to `__errno()`.
- Stores the error into thread-local errno.
- Returns `-1` in `%rax`.

## Notes
This implementation always uses `__errno()` rather than a non-reentrant global errno path.
