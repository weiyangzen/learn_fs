# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigreturn.S

Implements SPARC64 compatibility `sigreturn`.

It loads `SYS_compat_13_sigreturn13`, traps through `ST_SYSCALL`, and enters `ERROR()` if the syscall returns.

This is a direct legacy signal-return entry.
