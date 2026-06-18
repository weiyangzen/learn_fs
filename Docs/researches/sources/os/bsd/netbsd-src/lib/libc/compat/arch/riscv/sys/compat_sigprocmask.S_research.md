# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigprocmask.S

Defines RISC-V compatibility `sigprocmask`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigprocmask13`.

This is a minimal syscall alias.
