# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/fork.S

This file implements PowerPC `__fork`. It invokes the `fork` syscall and converts the kernel’s `%r4` parent/child flag so the child returns zero and the parent returns the child PID in `%r3`.

It relies on `_SYSCALL` for trap and error handling. There is no extra state.
