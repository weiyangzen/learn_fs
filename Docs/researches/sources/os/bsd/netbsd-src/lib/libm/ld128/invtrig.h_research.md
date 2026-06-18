# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.h

This header declares and aliases the shared ld128 inverse trig constants, defines precision thresholds, and provides inline polynomial evaluators.

Key thresholds include `ASIN_LINEAR`, `ACOS_CONST`, `ATAN_CONST`, and `ATAN_LINEAR`, all derived from `LDBL_MAX_EXP` for 113-bit precision. `THRESH` represents 0.95 in the long-double mantissa format.

It remaps common names like `pS0`, `atanhi`, and `pi_lo` to internal `_ItL_*` symbols to avoid namespace collisions. Inline helpers `P()`, `Q()`, `T_even()`, and `T_odd()` evaluate the approximation polynomials.

This is shared infrastructure, not a standalone implementation.
