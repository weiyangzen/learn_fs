# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/SYS.h

This header defines PowerPC64 syscall wrapper macros. Unlike 32-bit PowerPC, it inlines the `__cerror` behavior in `_DO_CERROR()` because branching to `__cerror` is unreliable with the PowerPC64 ABI.

The macros load syscall numbers into `%r0`, execute `sc`, use summary overflow to detect errors, and either return or inline errno storage and `-1` returns. Reentrant builds call `__errno`; non-reentrant builds store through TOC-addressed `errno`.
