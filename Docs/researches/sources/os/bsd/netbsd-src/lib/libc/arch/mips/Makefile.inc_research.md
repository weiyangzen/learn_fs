# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/Makefile.inc

This make include configures top-level MIPS libc architecture sources. It adds `__sigtramp2.S`, includes the current directory for generated headers, supplies `assym.h` CPP flags, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

For softfloat MIPS builds it adds IEEE754 unsigned conversion helpers, with extra long-double/quad helpers for MIPS64 non-o32 ABIs. The file is build-policy glue keyed to `MACHINE_MIPS64`, `CPUFLAGS`, and ABI selection.
