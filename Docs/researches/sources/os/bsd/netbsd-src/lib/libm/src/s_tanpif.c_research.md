# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpif.c

Implements float `tanpif(x)`, the single-precision counterpart to `tanpi()`. It uses float split-pi constants for tiny input, an inline `__kernel_tanpif()` using `__kernel_tandf()`, and float-specific integer-range thresholds.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `k_tandf.c`, `GET_FLOAT_WORD`, `SET_FLOAT_WORD`, `FFLOORF`, and `copysignf()`.

Special cases mirror the double version: signed zero for integer arguments, signed infinity at half-integers, and NaN for infinities/NaNs.
