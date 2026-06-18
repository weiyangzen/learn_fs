# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/ptrace.S

This file implements MIPS `ptrace`. It clears global `errno` before making the syscall, because `ptrace` can return `-1` successfully, then traps and uses `a3` to branch to `__cerror` on failure.

A comment marks the non-reentrant direct `errno` store as “BOGUS,” reflecting that this assembly path does not use `__errno`. This routine is semantically important for callers that inspect errno after `ptrace`.
