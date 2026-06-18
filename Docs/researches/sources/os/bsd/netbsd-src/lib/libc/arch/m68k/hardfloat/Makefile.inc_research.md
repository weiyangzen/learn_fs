# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/Makefile.inc

This m68k hardfloat make fragment adds `modf`, fenv accessors, and a suite of FPU-backed libgcc helper routines. These helpers let otherwise softfloat-style programs use the m68k FPU for arithmetic, conversion, and comparison operations.
