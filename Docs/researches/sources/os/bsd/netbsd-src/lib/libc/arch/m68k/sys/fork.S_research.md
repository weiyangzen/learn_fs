# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/fork.S

This file implements internal `__fork` around the kernel `fork` syscall. After a successful syscall it transforms the kernel’s parent/child indicator in `%d1` so the child returns zero and the parent returns the child PID.

Errors are handled by the `_SYSCALL` macro through `CERROR`. This is pure fork ABI adaptation for libc.
