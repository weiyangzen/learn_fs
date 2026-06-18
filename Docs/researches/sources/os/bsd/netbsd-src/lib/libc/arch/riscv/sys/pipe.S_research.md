# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer in `a2`, invokes the kernel `pipe` syscall, stores descriptors from `a0` and `a1` into the two integer slots, returns zero, and jumps to `__cerror` on failure.

It adapts the RISC-V register-return convention to the C `pipe(int[2])` API.
