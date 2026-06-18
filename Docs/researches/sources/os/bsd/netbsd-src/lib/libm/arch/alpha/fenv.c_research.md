# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/fenv.c

Alpha floating-point environment support. It uses `sysarch(ALPHA_FPGETMASK/FPSETMASK)` for trap masks and Alpha FPCR moves for environment state.

Only environment and exception-enable routines are real functions here; other fenv operations are static inline in `fenv.h`, so alpha uses a custom export-symbol list.
