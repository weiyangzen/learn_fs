# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the caller’s output pointer, invokes the kernel `pipe` syscall, stores returned descriptors from `r11` and `r12` into the two integers, clears `r11`, and returns zero.

It converts the kernel’s multiple-register return convention into the C API’s array convention.
