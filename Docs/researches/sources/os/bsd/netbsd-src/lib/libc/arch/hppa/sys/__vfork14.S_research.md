# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__vfork14.S

This HPPA `__vfork14` wrapper avoids stack saves because the child may disturb the stack. It preserves the return pointer in `%t4`, uses the syscall gateway directly, restores `%rp` in the branch delay path, and normalizes parent/child return values with `%ret1`.
