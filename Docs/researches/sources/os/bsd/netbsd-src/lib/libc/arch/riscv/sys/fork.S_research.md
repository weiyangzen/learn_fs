# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/fork.S

This file implements RISC-V `__fork`. It issues the `fork` syscall, jumps to `__cerror` on failure, then converts the kernel’s `a1` parent/child indicator so the child returns zero and the parent returns the child PID in `a0`.

It is standard fork return-value adaptation for RISC-V libc.
