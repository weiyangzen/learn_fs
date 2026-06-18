# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_truncf.c

Implements float `truncf()` by clearing fractional bits in the IEEE single-precision word. It handles `|x| < 1` by returning signed zero, leaves already-integral values unchanged, and returns `x+x` for Inf/NaN.

Important dependencies: `math.h`, `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Like the double version, it uses a large constant to raise inexact when the result differs from the input.
