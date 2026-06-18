# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__clone.S

This file implements PowerPC `__clone` and weak `clone`. It validates function and stack arguments, saves the function pointer, rearranges syscall arguments to `(flags, stack)`, invokes `__clone`, and on error branches to `__cerror`.

The parent returns directly; the child moves the saved function pointer into LR, calls it with the supplied argument, and calls `_exit` with the result. PIC builds set up the TOC before calling `_exit`.
