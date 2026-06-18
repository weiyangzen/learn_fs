# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/cerror.S

This file defines the m68k syscall error handler `CERROR`. It writes the kernel error value from `%d0` into thread-local `errno` through `__errno` in reentrant builds, or global `errno` otherwise, then returns `-1` in `%d0` and `%d1`.

It also handles PIC and SVR4 ABI details. Almost every m68k syscall wrapper depends on this path for consistent errno and return-value semantics.
