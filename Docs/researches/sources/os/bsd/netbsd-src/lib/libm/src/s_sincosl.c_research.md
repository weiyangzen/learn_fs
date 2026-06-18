# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosl.c

Implements long-double `sincosl()` or falls back to double `sincos()` when long double is absent.

Key behavior: uses long-double kernels and ld80/ld128 `rem_pio2l` reduction; handles zero/subnormal as `sin=x`, `cos=1`; sets both outputs to NaN for Inf/NaN; maps quadrants.

Important dependencies: `k_sincosl.h`, `../ld80/e_rem_pio2l.h`, `../ld128/e_rem_pio2l.h`, and `math_private.h`.

Notable risks: backend selection and quadrant sign swapping are precision- and format-sensitive.
