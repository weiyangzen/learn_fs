# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/pipe.S

This file implements `_pipe` with weak public alias `pipe`. After the kernel returns two file descriptors in `%d0` and `%d1`, it stores them into the user-provided `int[2]`, clears `%d0`, and returns zero.

It is a classic BSD syscall adaptation where multiple register return values are converted into the C API’s output array. Failure handling is provided by `_SYSCALL`.
