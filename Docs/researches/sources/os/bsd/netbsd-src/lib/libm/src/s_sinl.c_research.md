# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinl.c

Implements long-double `sinl()` using ld80 or ld128 kernel and range-reduction sources.

Key behavior: returns `x` for zero/subnormal, NaN for Inf/NaN, uses a `pi/4` fast path, and dispatches by quadrant after `__ieee754_rem_pio2l()`.

Important dependencies: `../ld80/e_rem_pio2l.h`, `../ld80/k_sinl.c`, `../ld128/e_rem_pio2l.h`, `../ld128/k_sinl.c`, and `math_private.h`.

Notable risks: direct inclusion of backend C files means compile-time format selection controls the implementation.
