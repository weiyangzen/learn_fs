# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log2.c

This file implements `__ieee754_log2(double x)`.

It reuses the fdlibm natural-log reduction and polynomial approximation, but returns the exponent `k` plus the reduced logarithm divided by `ln2`. Small reduced arguments use a short correction; other inputs use the same `s = f/(2+f)` polynomial split used by `log`.

Special cases cover zero, negative input, subnormals, Inf, and NaN. Dependencies are `math_private.h` bit access and `scalbn`-style exponent handling through direct word manipulation.
