# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/SYS.h

This header defines the MIPS libc syscall wrapper macros. It includes syscall numbers and MIPS assembly helpers, emits `.abicalls` and GP setup/restore behavior for PIC ABIs, and defines `SYSTRAP`, `RSYSCALL`, `WSYSCALL`, `PSEUDO`, and `PSEUDO_NOERROR`.

The generated wrappers use `v0` for syscall number/results and `a3` as the kernel error indicator, tail-calling `__cerror` when needed. This header is the core ABI contract for nearly every MIPS syscall assembly file in this group.
