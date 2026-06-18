# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fma.c

Implements software double `fma(x,y,z)` with single-rounding semantics using double-double arithmetic.

Key behavior: handles zeros, infinities, NaNs, and signed-zero cancellation specially; scales operands with `frexp`; temporarily forces round-to-nearest for exact product/sum; restores directed rounding behavior; handles subnormal results with sticky-bit adjustment.

Important dependencies: `fenv.h`, `math_private.h`, `frexp`, `ldexp`, `ilogb`, `nextafter`, `feraiseexcept`, and word64 macros.

Notable risks: depends on FPU precision and rounding-mode control; hardware FMA is preferable where available.
