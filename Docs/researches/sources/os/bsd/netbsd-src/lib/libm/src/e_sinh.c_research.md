# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinh.c

This file implements double `__ieee754_sinh(double x)`.

It handles Inf/NaN by returning `x+x`, preserves sign through a half multiplier, returns tiny inputs unchanged while raising inexact as appropriate, uses `expm1(|x|)` for `|x| < 22`, uses `0.5*exp(|x|)` up to `log(maxdouble)`, uses split half-exponent multiplication near overflow, and overflows with `x*shuge` beyond the threshold.

Dependencies include `expm1`, `__ieee754_exp`, `fabs`, and double word macros.
