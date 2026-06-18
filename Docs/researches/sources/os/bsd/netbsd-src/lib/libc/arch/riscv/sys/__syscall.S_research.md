# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__syscall.S

This file implements RISC-V `__syscall`, with strong `_syscall` and weak `syscall` aliases. It invokes the kernel `__syscall` entry using the generic `SYSTRAP` macro, jumps to `__cerror` on error, and returns on success.

Unlike some other architectures, no local argument shuffling is present here. The kernel ABI handles the generic syscall convention through the `__syscall` number.
