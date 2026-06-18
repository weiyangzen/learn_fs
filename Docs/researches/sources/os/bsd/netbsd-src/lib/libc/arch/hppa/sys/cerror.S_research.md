# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/cerror.S

This HPPA syscall error handler stores the error code from `%t1` into thread-local `errno` via `__errno` in reentrant builds or into global `errno` otherwise. It returns `-1` in both `%ret0` and `%ret1`.
