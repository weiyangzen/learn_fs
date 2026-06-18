# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/fork.S

This file implements or1k `__fork`. After `_SYSCALL(__fork,fork)` succeeds, it transforms the kernel’s parent/child flag in `r12` so the child returns zero and the parent returns the child PID in `r11`.

It is minimal fork ABI glue, relying on the syscall macro for trap and error handling.
