# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/ptrace.S

## Summary
Implements SH3 `ptrace()` with errno pre-clear semantics.

## Key Details
- Clears `errno` before invoking `SYS_ptrace`.
- Preserves syscall arguments while locating `errno` in reentrant builds.
- Supports PIC and non-PIC errno access.
- Jumps to `cerror` if the trap reports failure.

## Notes
Pre-clearing errno is needed because successful `ptrace` calls can legitimately return `-1`.
