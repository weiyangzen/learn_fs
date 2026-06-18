# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigaction.S

Defines SH3 compatibility `sigaction`.

It emits the standard signal-header warning and maps to `compat_13_sigaction13`.

This is a minimal signal ABI veneer.
