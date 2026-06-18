# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/_lwp_getprivate.S

This file defines the public `_lwp_getprivate` syscall wrapper. It invokes `SYSCALL(_lwp_getprivate)` and returns, with an SVR4 ABI path copying the pointer result from `%d0` into `%a0`.

It is used directly and by `__m68k_read_tp` for thread-private data access. Its behavior is otherwise standard m68k libc syscall wrapping.
