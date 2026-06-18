# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigreturn14.S

Implements SPARC64 `__sigreturn14`.

It loads `SYS_compat_16___sigreturn14`, traps via `ST_SYSCALL`, and enters `ERROR()` if control returns.

Used by the legacy sigcontext trampoline.
