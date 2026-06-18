# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/cerror.S

This IA-64 syscall error handler saves return state, calls `__errno`, stores the error code, restores `ar.pfs` and `rp`, and returns `-1`.
