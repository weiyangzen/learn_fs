# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/ptrace.S

## Summary
Implements SPARC `ptrace()` with errno pre-clear behavior.

## Key Details
- Clears errno before invoking `SYS_ptrace`.
- Uses `__errno()` in reentrant builds.
- Uses global `errno` in non-reentrant builds, with PIC support.
- Returns normally on success or branches to `ERROR()` on failure.

## Notes
Pre-clearing errno handles successful `ptrace` calls that return `-1`.
