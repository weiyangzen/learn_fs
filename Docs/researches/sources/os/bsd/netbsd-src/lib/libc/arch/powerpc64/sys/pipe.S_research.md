# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer, invokes `pipe`, stores file descriptors from `%r3` and `%r4`, returns zero, and uses inline error handling on failure.

It adapts the kernel’s two-register result to the C API’s output array.
