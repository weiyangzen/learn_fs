# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/pipe.S

This IA-64 `pipe` wrapper saves the caller's output pointer, invokes the syscall, stores returned descriptors from `ret0` and `ret1`, and returns zero. A comment notes parameter passing should be revisited.
