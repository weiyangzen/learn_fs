# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atanh.c

Wrapper for double `atanh()`. It delegates to `__ieee754_atanh(x)` and maps `|x| > 1` to error code `30` and `|x| == 1` to error code `31` outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `fabs()`, and `isnan()`.

NaNs and IEEE mode return the raw IEEE result.
