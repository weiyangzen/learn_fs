# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__syscall.S

This raw i386 `__syscall` entry pops the return address, syscall number, and alignment/junk word to match the quad-aligned calling convention, invokes `int $0x80`, restores stack shape, and branches to the syscall error path on carry.
