# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cosf.c

Implements float `cosf()` with float kernels and float argument reduction.

Key behavior: uses `__kernel_cosf()` for small inputs, returns NaN for Inf/NaN, and dispatches by quadrant to sine or cosine kernels.

Important dependencies: `math_private.h`, `__kernel_cosf`, `__kernel_sinf`, and `__ieee754_rem_pio2f`.

Notable risks: shares the same quadrant and range-reduction sensitivities as `cos()`, but with float thresholds.
