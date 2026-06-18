# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/syscall.S

This file implements `_syscall` and weak alias `syscall`, the generic runtime syscall entry point. It clears `%d0`, executes `trap #0`, branches to `CERROR` on carry/error, and otherwise returns the kernel result.

Unlike named syscall wrappers, the syscall number is supplied by the caller using the generic convention. This is low-level ABI glue for code that invokes arbitrary syscall numbers.
