# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cosl.c

Implements `cosl()` for long double, including the ld80 or ld128 range reducer and kernel source directly according to `LDBL_MANT_DIG`.

Key behavior: returns `1.0` for zero/subnormal inputs, NaN for Inf/NaN, uses a `pi/4` fast path, and dispatches by quadrant after `__ieee754_rem_pio2l()`.

Important dependencies: `../ld80/e_rem_pio2l.h`, `../ld80/k_cosl.c`, `../ld128/e_rem_pio2l.h`, `../ld128/k_cosl.c`, and `math_private.h`.

Notable risks: compile-time inclusion couples this file to the exact selected long-double backend.
