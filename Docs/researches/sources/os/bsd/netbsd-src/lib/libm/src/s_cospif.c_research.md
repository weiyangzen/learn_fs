# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospif.c

Implements float `cospif(x)` using float/double kernels for `cos(pi*x)`. It mirrors `s_cospi.c` with float thresholds and `FFLOORF`.

Key behavior: returns 1 for tiny inputs while raising inexact when appropriate, returns 0 at half-integers, tracks integer parity up to `2^24`, and produces invalid NaN for Inf/NaN.

Important dependencies: `k_cosdf.c`, `k_sindf.c`, `math_private.h`, and `M_PI`.

Notable risks: kernel macros multiply by `M_PI`; accuracy differs from pure table-based pi reduction.
