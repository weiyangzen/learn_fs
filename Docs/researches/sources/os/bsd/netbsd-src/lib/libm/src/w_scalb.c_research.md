# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_scalb.c

Wrapper for legacy `scalb()`, with signature depending on `_SCALB_INT`. It delegates to `__ieee754_scalb()` and maps overflow/underflow to legacy errors outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `<errno.h>`, `finite()`, and `isnan()`.

It sets `errno = ERANGE` when the exponent argument is nonfinite in the non-integer signature variant.
