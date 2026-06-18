# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaf.c

Implements software float `fmaf()` by evaluating the multiply-add in double and correcting double-rounding halfway cases.

Key behavior: returns the double result for common cases, NaNs, exact sums, and non-round-to-nearest modes; for halfway inexact cases, recomputes toward zero and adjusts the low word if needed.

Important dependencies: `fenv.h`, `math_private.h`, `EXTRACT_WORDS`, and `SET_LOW_WORD`.

Notable risks: changes rounding mode temporarily and includes a volatile workaround for compiler common-subexpression issues.
