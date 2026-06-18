# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/Makefile.inc

This make include adds PowerPC64 syscall-directory sources `__sigaction14_sigtramp.c` and `__sigtramp2.S`. It is narrow build metadata for signal handling support.

The explicit inclusion suggests signal trampoline handling differs enough from the top-level architecture include to need sys-directory source selection.
