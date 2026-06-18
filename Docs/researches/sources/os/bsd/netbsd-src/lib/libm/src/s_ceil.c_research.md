# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ceil.c

Implements double `ceil()` by direct IEEE-754 word manipulation. It masks fractional bits, increments positive nonintegral values as needed, preserves signed zero behavior, and raises inexact through the `huge + x` idiom.

Key behavior: returns infinities/NaNs as `x+x`, leaves already integral values unchanged, and aliases `ceill` to `ceil` when there is no real long double.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: assumes IEEE double word layout and relies on volatile-style arithmetic side effects for exception flags.
