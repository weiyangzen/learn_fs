# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigaction.S

Defines MIPS compatibility `sigaction`.

It emits a compatibility warning and maps to `compat_13_sigaction13`.

This preserves old signal action struct/layout ABI.
