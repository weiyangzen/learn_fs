# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/ptrace.S

This file implements `ptrace` with special errno pre-clearing. Before issuing the syscall it sets thread-local or global `errno` to zero, then performs the `ptrace` trap and branches to `CERROR` on failure.

The pre-clear matters because `ptrace` can legitimately return `-1` as data on success, so callers distinguish success from failure by checking errno. The implementation carries PIC and reentrant errno handling.
