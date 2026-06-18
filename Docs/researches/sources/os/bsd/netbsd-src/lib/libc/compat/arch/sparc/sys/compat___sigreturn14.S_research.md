# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigreturn14.S

Implements SPARC `__sigreturn14`.

It loads `SYS_compat_16___sigreturn14` into `%g1`, traps through `ST_SYSCALL`, and falls into `ERROR()` if the syscall returns.

This supports the old sigcontext trampoline path.
