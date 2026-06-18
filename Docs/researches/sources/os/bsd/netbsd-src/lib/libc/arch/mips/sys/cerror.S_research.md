# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/cerror.S

This file defines MIPS `__cerror`, the common syscall error return path. In reentrant builds it saves return state, calls `__errno`, writes the saved error value, restores GP/RA as needed, and returns `-1` in both `v0` and `v1`.

In non-reentrant builds it stores the error directly in global `errno`. This routine is central to MIPS syscall wrappers and is especially sensitive to PIC GP setup for o32/n32/n64.
