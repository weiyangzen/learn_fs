# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderl.c

This file implements public `remainderl(long double x, long double y)` as a thin wrapper around `remquol`.

It declares a local `int quo`, calls `remquol(x, y, &quo)` when long double exists, and falls back to double `remquo` otherwise. It contains no independent reduction algorithm.

Dependencies are `<math.h>` and availability of `remquol` or `remquo`.
