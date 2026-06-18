# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/pipe.S

This i386 `pipe` wrapper invokes the syscall, stores returned file descriptors from `%eax` and `%edx` into the caller's array, and returns zero.
