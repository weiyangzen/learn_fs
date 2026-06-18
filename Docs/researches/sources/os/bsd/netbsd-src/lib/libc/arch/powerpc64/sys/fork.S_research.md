# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/fork.S

This file implements PowerPC64 `__fork`. It calls the `fork` syscall and adjusts `%r4`/`%r3` so the child returns zero and the parent returns the child PID.

It is the same return-value transformation pattern used by the PowerPC vfork/fork wrappers.
