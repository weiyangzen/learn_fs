# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_trunc.c

Implements double `trunc()` by direct IEEE bit manipulation. It clears fractional significand bits according to the unbiased exponent, preserves signed zero for `|x| < 1`, returns integral values unchanged, and returns `x+x` for Inf/NaN.

Important dependencies: `math.h`, `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

The `huge + x > 0.0` checks intentionally raise inexact when truncation changes a nonzero finite value.
