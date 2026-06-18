# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_msgctl.S

Defines RISC-V compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is a simple public-domain compatibility wrapper.
