# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/pipe.S

This HPPA `pipe` wrapper saves the output array pointer, invokes the syscall, stores returned descriptors from `%ret0` and `%ret1`, and returns zero.
