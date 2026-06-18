# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/ptrace.S

This file implements RISC-V `ptrace` with errno pre-clearing. Reentrant builds save arguments and return address, call `__errno`, clear errno, restore arguments, then invoke the syscall; non-reentrant builds clear global `errno` via PC-relative addressing.

The pre-clear allows callers to distinguish successful `-1` returns from errors. On syscall failure, the wrapper jumps to `__cerror`.
