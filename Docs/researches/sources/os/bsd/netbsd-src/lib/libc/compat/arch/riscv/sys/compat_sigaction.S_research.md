# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigaction.S

Defines RISC-V compatibility `sigaction`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigaction13`.

This preserves old signal action ABI names.
