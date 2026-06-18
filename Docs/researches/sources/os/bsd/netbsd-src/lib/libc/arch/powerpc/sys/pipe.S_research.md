# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer, invokes the `pipe` syscall, stores returned descriptors from `%r3` and `%r4`, returns zero, and branches to `__cerror` on failure.

It adapts multiple register returns into the C `int fildes[2]` API.
