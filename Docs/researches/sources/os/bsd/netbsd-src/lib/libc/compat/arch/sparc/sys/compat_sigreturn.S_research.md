# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigreturn.S

Implements SPARC compatibility `sigreturn`.

It loads `SYS_compat_13_sigreturn13` into `%g1`, traps via `ST_SYSCALL`, and enters `ERROR()` if it returns.

This is a direct old signal-return syscall entry.
