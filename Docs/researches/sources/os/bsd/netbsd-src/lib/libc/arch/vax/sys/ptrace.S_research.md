# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/ptrace.S

## Summary
Implements VAX `ptrace()` with errno pre-clear behavior.

## Key Details
- Clears thread-local or global errno before the syscall.
- Calls `SYS_ptrace`.
- Returns on success.
- Jumps to `CERROR+2` on carry-set failure.

## Notes
Pre-clearing errno permits callers to disambiguate a valid `-1` result from failure.
