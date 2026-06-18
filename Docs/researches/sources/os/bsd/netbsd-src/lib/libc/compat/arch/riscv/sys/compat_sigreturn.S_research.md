# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigreturn.S

Defines RISC-V compatibility `sigreturn`.

It emits a warning and maps to `compat_13_sigreturn13`.

This is a minimal legacy signal-return veneer.
