# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_missing.c

Defines compatibility symbols that autoconf or old code may probe without including the modern standard headers.

It declares warning references for `sigaction`, `sigpending`, `sigprocmask`, and `sigsuspend`, then implements these public symbols as forwarding C functions to modern/internal NetBSD signal APIs: `__sigaction_siginfo`, `__sigpending14`, `__sigprocmask14`, and `__sigsuspend14`.

This is PowerPC64-specific ABI surface completion for old signal APIs.
