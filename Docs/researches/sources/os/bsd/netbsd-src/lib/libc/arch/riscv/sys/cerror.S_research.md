# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/cerror.S

This file defines protected RISC-V `__cerror`. In reentrant builds it saves `ra` and the error value, calls `__errno`, writes errno, restores state, and returns `-1` in `a0` and `a1`.

In non-reentrant builds it uses PC-relative addressing to store the error into global `errno`. This is the shared error path for all RISC-V syscall wrappers.
