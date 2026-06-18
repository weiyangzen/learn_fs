# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It invokes the `pipe` syscall, stores returned descriptors from `v0` and `v1` into the user `int[2]` pointed to by `a0`, returns zero on success, and tail-calls `__cerror` on failure.

It converts the kernel’s multiple-register return convention into the C API’s output-buffer convention.
