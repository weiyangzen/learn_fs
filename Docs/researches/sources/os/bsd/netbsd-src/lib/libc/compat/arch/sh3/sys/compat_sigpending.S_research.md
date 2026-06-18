# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigpending.S

Implements SH3 compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores the returned mask into `@r4`, clears `r0`, and returns.

This adapts the legacy integer mask result to the caller’s pointer output.
