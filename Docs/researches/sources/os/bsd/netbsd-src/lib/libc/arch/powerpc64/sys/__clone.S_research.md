# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__clone.S

This file implements PowerPC64 `__clone` and weak `clone`. It validates function and stack pointers, saves the function pointer, rearranges arguments for the kernel `__clone(flags, stack)` call, and uses inline syscall error handling via `BRANCH_TO_CERROR()`.

The parent returns normally; the child calls the function with the argument and then calls `_exit`. The code mirrors the 32-bit PowerPC logic but uses PowerPC64 ABI support from `SYS.h`.
