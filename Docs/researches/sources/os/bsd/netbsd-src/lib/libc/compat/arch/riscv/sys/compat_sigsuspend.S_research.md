# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigsuspend.S

Defines RISC-V compatibility `sigsuspend`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigsuspend13`.

This is a simple legacy signal-mask wrapper.
