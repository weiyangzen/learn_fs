# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__vfork14.S

This file implements RISC-V `__vfork14`. It performs the syscall, jumps to `__cerror` on failure, then adjusts `a1` and masks `a0` so the child returns zero and the parent returns the child PID.

The wrapper mirrors `fork.S` return-value logic but uses the `__vfork14` syscall number.
