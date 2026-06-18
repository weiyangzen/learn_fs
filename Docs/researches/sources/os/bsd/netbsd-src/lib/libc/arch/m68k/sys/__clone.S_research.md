# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__clone.S

This file implements the m68k `__clone` wrapper and weak `clone` alias. It validates that the function pointer and stack pointer are non-NULL, prepares the child stack with the argument and fake syscall frame, invokes the `__clone` system call, and distinguishes parent from child by the returned value.

In the child path it calls the supplied function and then calls `_exit` with that return value. On invalid inputs or syscall failure it routes through `CERROR`, making this wrapper both ABI glue and error-policy enforcement.
