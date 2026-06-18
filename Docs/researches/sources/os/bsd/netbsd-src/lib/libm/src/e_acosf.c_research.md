# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosf.c

Implements fdlibm kernel `__ieee754_acosf(float)`.

Key behavior:
- Float conversion of `e_acos.c`.
- Uses float constants and bit macros.
- Splits into `|x| < 0.5`, `x < -0.5`, and `x > 0.5` cases.
- Uses `__ieee754_sqrtf` and truncates part of `sqrt` for correction in the `x > 0.5` case.
