# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpif.c

Implements float `sinpif(x)` as the float counterpart to `sinpi()`.

Key behavior: preserves signed zero, uses split float pi for tiny values, maps fractional intervals to sine/cosine kernels, reduces integer parts with `FFLOORF`, flips sign by parity, returns signed zero for large integral values, and invalid NaN for Inf/NaN.

Important dependencies: `k_cosdf.c`, `k_sindf.c`, `math_private.h`, `copysignf`, and `FFLOORF`.

Notable risks: kernel wrappers multiply by `M_PI`, and parity is only recoverable below the float integer-precision limit.
