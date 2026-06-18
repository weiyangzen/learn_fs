# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2l.c

Implements long-double `atan2l`.

Key behavior:
- With long double support, inspects exponent/sign and significand fields directly.
- Handles NaNs via `nan_mix`, signed zeros, zero `x`, infinities, and quadrants.
- Uses format-specific `invtrig.h` constants for `pio2_hi`, `pio2_lo`, and `pi_lo`.
- Avoids unsafe division based on exponent difference and `LDBL_MANT_DIG`.
- Falls back to double `atan2` when long double support is absent.
