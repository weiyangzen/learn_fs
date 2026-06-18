# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/Makefile.inc

Lists PowerPC64 compatibility syscall sources.

The included objects cover `msgctl`, `__semctl`, `shmctl`, `quotactl`, and `compat_missing.c`.

This architecture uses C shims for several missing legacy signal symbols instead of the fuller assembly set present on 32-bit PowerPC.
