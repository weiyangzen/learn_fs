# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/pipe.S

This ARM `pipe` wrapper saves the caller's `int fd[2]` pointer, invokes the `pipe` syscall, stores returned descriptors from `r0` and `r1` into the array, and returns zero on success.
