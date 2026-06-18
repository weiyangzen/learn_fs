# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/cerror.S

This is the ARM syscall error path. It stores the kernel error value into thread-local `errno` via `__errno` for reentrant builds, or into the global `errno` otherwise, then returns `-1` in both `r0` and `r1` for scalar and 64-bit return conventions.
