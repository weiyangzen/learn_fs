# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_Ovfork.S

Implements x86_64 compatibility `vfork`.

It pops the return address into `%r9`, invokes the `vfork` syscall, fixes parent/child return values using `%edx` and `%eax`, and jumps to the saved return address. The error path restores the return address and jumps to `CERROR`, with PIC support.

This preserves old `vfork` calling behavior.
