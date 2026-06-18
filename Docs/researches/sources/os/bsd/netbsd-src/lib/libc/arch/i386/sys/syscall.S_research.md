# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/syscall.S

This i386 `_syscall` entry pops the return address and runtime syscall number, invokes `int $0x80`, restores stack consistency, and branches to `__cerror` on carry. It weakly aliases public `syscall` to `_syscall`.
