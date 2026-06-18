# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/Makefile.inc

This make include configures 32-bit PowerPC libc architecture sources. It adds `__sigtramp2.S` and `powerpc_initfini.c`, includes the architecture directory, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

The important integration point is `powerpc_initfini.c`, which provides cache-line data used by optimized memory routines. Source selection here affects both syscall/signal ABI code and string routine performance.
