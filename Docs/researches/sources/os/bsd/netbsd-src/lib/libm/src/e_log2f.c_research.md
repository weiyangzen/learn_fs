# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log2f.c

This file implements `__ieee754_log2f(float x)`.

It is the float counterpart of `e_log2.c`: subnormals are scaled, the input is normalized around 1, a polynomial approximates the reduced log, and the result is converted to base 2 by dividing by `ln2` and adding the extracted exponent.

Dependencies are float constants, `GET_FLOAT_WORD`/`SET_FLOAT_WORD`, and standard arithmetic.
