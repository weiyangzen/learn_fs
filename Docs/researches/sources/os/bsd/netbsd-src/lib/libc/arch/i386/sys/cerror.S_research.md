# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/cerror.S

This i386 syscall error handler saves the kernel error from `%eax`, calls `__errno`, stores the error code through the returned pointer, and returns `-1` in both `%eax` and `%edx`.
