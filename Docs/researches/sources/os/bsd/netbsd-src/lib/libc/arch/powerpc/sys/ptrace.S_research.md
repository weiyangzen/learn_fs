# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/ptrace.S

This file implements PowerPC `ptrace` with errno pre-clearing. Reentrant builds save call arguments, call `__errno`, clear errno, restore arguments, then issue the syscall; non-reentrant builds clear global `errno` directly.

The pre-clear is required because `ptrace` can return `-1` on success. The implementation includes PIC TOC setup and careful stack frame offsets for the saved arguments.
