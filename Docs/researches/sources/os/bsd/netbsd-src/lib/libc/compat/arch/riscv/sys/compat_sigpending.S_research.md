# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigpending.S

Defines RISC-V compatibility `sigpending`.

It emits the standard compatibility warning and maps directly to `compat_13_sigpending13`.

Unlike older architectures, this file does not perform pointer-to-integer mask adaptation in assembly.
