# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/fenv.c

m68k fenv wrapper file. It exposes weak aliases and extern inline definitions from `fenv.h`, requiring C99 inline semantics. The actual operations are provided by the architecture header inline implementations.
