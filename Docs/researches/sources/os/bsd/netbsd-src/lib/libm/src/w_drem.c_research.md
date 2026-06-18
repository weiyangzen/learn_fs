# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_drem.c

Implements legacy double `drem(x, y)` as a direct call to `remainder(x, y)`.

Important dependency: `<math.h>`.

All behavior, including exceptions and NaN handling, is inherited from `remainder()`.
