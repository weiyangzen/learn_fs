# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/syscall.S

This file provides the o32 MIPS `syscall` / `_syscall` wrapper when `__mips_o32` is defined. It is built via `WSYSCALL(syscall,_syscall)`, which creates a weak public alias and a strong internal implementation.

For non-o32 ABIs, `__syscall.S` provides the aliases instead. The split reflects ABI-specific syscall argument and symbol conventions.
