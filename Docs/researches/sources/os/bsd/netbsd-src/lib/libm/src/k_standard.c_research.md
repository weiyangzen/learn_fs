# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_standard.c

This file implements fdlibm compatibility error handling through `__kernel_standard(double x, double y, int type)`.

It maps numeric error codes to historical libm error behavior for domain, singularity, overflow, underflow, and total-loss cases across functions such as `acos`, `asin`, `atan2`, `hypot`, `exp`, Bessel functions, `lgamma`, `log`, `pow`, `sinh`, `sqrt`, `fmod`, `remainder`, `acosh`, `atanh`, `scalb`, and `log2`. Float variants are represented by type codes offset by 100, and some long-double cases by 200-series codes.

Behavior depends on `_LIB_VERSION`: IEEE, POSIX, SVID, and X/Open-style handling differ in return values, `errno`, `matherr()` dispatch, and optional stderr messages. Dependencies include `math.h`, `math_private.h`, `<errno.h>`, and either `fputs` or `write`.
