# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1.c

Implements double `expm1(x)` with FDLIBM argument reduction and a cancellation-resistant rational approximation for `exp(x)-1`.

Key behavior: handles huge/nonfinite inputs, reduces by `k*ln2`, evaluates a polynomial in the primary interval, and uses multiple scaling cases for accurate reconstruction.

Important dependencies: `math_private.h`, high-word access macros, and split `ln2` constants.

Notable risks: reconstruction branches are delicate; algebraic simplification can break near-zero and large-negative accuracy.
