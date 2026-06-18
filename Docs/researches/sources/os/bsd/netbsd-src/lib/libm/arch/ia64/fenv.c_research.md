# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/ia64/fenv.c

IA-64 fenv wrapper file. Most fenv operations are provided as C99 extern inline definitions from `fenv.h`; this file defines `__fe_dfl_env`, weak aliases, inline declarations, and a non-inline `feupdateenv()` that saves FPSR, restores the requested environment, and reraises saved exceptions.
