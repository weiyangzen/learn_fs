# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/ptrace.S

## Summary
Implements SPARC64 `ptrace()`.

## Key Details
- Calls `__errno()` and clears errno before invoking `SYS_ptrace`.
- Uses a save/restore window around the errno call.
- Returns on success, otherwise dispatches to `ERROR()`.

## Notes
Unlike some other ports, this version always calls `__errno()` rather than a non-reentrant global path.
