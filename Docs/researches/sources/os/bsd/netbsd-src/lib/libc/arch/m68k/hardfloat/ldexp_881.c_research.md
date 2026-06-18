# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ldexp_881.c

This m68k FPU implementation of `ldexp` returns `value * 2**exp` by using the 68881 `fscalel` instruction in inline assembly.
