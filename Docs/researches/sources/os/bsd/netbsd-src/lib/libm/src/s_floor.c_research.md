# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floor.c

Implements double `floor()` by masking IEEE fractional bits and decrementing negative nonintegral values toward negative infinity.

Key behavior: raises inexact with `huge + x`, preserves signed zero, returns `x+x` for Inf/NaN, and aliases `floorl` when long double is absent.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: bit-level exponent/fraction logic is IEEE-specific.
