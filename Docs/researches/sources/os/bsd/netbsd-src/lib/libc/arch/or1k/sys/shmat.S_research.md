# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It contains no custom code beyond the macro-based syscall wrapper.

Its behavior is standard or1k trap and `__cerror` handling from `SYS.h`.
