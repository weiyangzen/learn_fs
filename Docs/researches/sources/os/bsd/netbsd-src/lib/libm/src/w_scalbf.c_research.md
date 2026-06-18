# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_scalbf.c

Wrapper for float `scalbf()`, with signature controlled by `_SCALB_INT`. It delegates to `__ieee754_scalbf()` and maps overflow and underflow to float legacy errors.

Important dependencies: `math.h`, `math_private.h`, `<errno.h>`, `finitef()`, and `isnanf()`.

Like the double wrapper, it sets `errno = ERANGE` for nonfinite float exponent arguments in the non-integer form.
