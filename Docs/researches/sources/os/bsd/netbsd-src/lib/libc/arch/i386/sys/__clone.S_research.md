# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__clone.S

This i386 `__clone` wrapper validates function and stack, pushes the child argument onto the new stack, invokes `__clone` with stack and flags, and distinguishes parent from child by the syscall return. The child calls the function and then `_exit` with its return value; invalid inputs route to `__cerror` with `EINVAL`.
