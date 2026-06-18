# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It has no local logic beyond macro expansion.

The resulting wrapper uses the standard PowerPC syscall and `__cerror` behavior.
