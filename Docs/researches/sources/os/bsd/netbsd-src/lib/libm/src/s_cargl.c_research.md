# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cargl.c

This file implements long-double complex argument `cargl(long double complex z)`.

The function simply returns `atan2l(cimagl(z), creall(z))`, delegating all quadrant, NaN, infinity, and signed-zero behavior to `atan2l`.

Dependencies are `<complex.h>` and `<math.h>`.
