# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanl.c

Implements `tanl()` for supported long-double formats. It directly returns `x` for zero/subnormal inputs, returns NaN for Inf/NaN, uses `__kernel_tanl()` for values below `pi/4`, and otherwise reduces with the long-double `__ieee754_rem_pio2l()` before choosing tangent or reciprocal-tangent kernel mode by quadrant.

Important dependencies: `namespace.h`, `<float.h>`, `math_private.h`, `../ld80` or `../ld128` `e_rem_pio2l.h` and `k_tanl.c`, plus `union ieee_ext_u`.

Special cases: long-double implementation is conditional on `__HAVE_LONG_DOUBLE`; otherwise it falls back to double `tan()`.
