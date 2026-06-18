# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It has no local logic beyond the syscall macro.

The generated wrapper uses RISC-V `ecall` and `__cerror` semantics from `SYS.h`.
