# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2.c

Implements double `exp2(x)` using Gal/Gal-Bachelis table-driven reduction. It uses a 256-entry table with small epsilon corrections and a degree-5 polynomial.

Key behavior: filters NaN, infinities, overflow, underflow, and tiny inputs; reduces via a `redux` rounding trick; scales by constructing powers of two and handles subnormal results by split scaling.

Important dependencies: `math_private.h`, `ieee_double_shape_type`, and `INSERT_WORDS`.

Notable risks: table values, `redux`, and low-word extraction are tightly tied to IEEE double representation.
