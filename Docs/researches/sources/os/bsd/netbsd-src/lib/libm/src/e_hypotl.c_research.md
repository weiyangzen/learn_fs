# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotl.c

Implements long-double `hypotl` when available, otherwise delegates to double `hypot`.

Key behavior:
- Uses long-double exponent/sign word macros and significand access.
- Sorts magnitudes and returns early for huge ratios.
- Handles infinities and NaNs while trying to quiet signaling NaNs.
- Scales very large and tiny inputs using long-double exponent manipulation.
- Uses compensated products with low significand parts cleared before `sqrtl`.
- Restores scale via exponent adjustment.
