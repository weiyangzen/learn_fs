# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/shmat.S

This file defines `shmat` via `RSYSCALL(shmat)`. It has no custom code beyond including `SYS.h`.

The wrapper uses standard MIPS syscall/error semantics from the macro layer. It exists because shared memory attachment needs an architecture-visible syscall entry.
