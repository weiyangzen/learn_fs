# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/SYS.h

This header defines 32-bit PowerPC syscall wrapper macros. It loads syscall numbers into `%r0`, executes `sc`, uses summary overflow (`bso` / `bnslr`) to detect errors, and branches to `__cerror`.

It supplies `_SYSCALL`, `PSEUDO`, `RSYSCALL`, and `WSYSCALL` forms for generated and hand-written wrappers. This is the shared ABI layer for the PowerPC syscall files.
