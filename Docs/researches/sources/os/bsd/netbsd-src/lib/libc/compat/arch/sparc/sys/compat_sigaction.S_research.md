# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigaction.S

Defines SPARC compatibility `sigaction`.

It emits the standard warning and maps to `compat_13_sigaction13`.

This preserves legacy signal-action ABI.
