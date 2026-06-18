# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/cerror.S

This file defines PowerPC `__cerror`. In reentrant builds it saves LR and callee-saved registers, calls `__errno`, stores the error value, restores state, and returns `-1` in `%r3` and `%r4`.

In non-reentrant builds it stores directly into global `errno`, with PIC and non-PIC paths. It is the shared error handler for PowerPC syscall wrappers.
