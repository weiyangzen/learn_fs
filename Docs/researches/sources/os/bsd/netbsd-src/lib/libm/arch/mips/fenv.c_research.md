# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mips/fenv.c

MIPS fenv wrapper file. It defines weak aliases and extern inline declarations from `fenv.h`, with `__fe_dfl_env` set to zero. Actual register manipulation is supplied by inline architecture definitions.
