# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtl.c

Implements `cbrtl(long double)` for supported long-double formats. It reduces exponent modulo 3, builds a float/double seed, applies Newton refinement, and rescales by the cube-root exponent factor.

Key behavior: handles zero, subnormal, infinity, and NaN explicitly; uses `ENTERI/RETURNI` for floating-point environment handling; supports `LDBL_MANT_DIG == 64` and `113`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `math_private.h`, `union ieee_ext_u`, `GET_EXPSIGN`, `SET_EXPSIGN`, and float word macros.

Notable risks: tightly coupled to IEEE extended/quad layout and to careful rounding-away steps before the final Newton iteration.
