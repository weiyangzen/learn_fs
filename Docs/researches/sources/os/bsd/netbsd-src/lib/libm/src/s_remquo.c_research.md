# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquo.c

Implements double `remquo()`, computing IEEE remainder and low quotient bits using shift-and-subtract arithmetic.

Key behavior: handles zero divisor, nonfinite inputs, NaNs, equal magnitudes, subnormal normalization, quotient accumulation, nearest-even fixup, signed zero remainder, and signed quotient output.

Important dependencies: `namespace.h`, `math_private.h`, `fabs`, and word extraction/insertion macros.

Notable risks: quotient and remainder logic is hand-coded on significand words; the signed zero and negative zero quotient case are subtle.
