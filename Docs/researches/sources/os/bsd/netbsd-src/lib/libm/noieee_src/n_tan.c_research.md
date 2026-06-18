# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tan.c

Implements no-IEEE `tan(double)`.

Key behavior:
- Rejects NaN/infinity by returning `x - x`.
- Reduces argument with `drem(x, PI)` into `[-pi/2, pi/2]`.
- Uses symmetry around `pi/4` to switch between `sin/cos` and `cos/sin`.
- Uses `sin__S` and `cos__C` polynomial macros from `trig.h`.
- Has a `national` special case for no-infinity hardware.

No `tanf` wrapper is defined in this file.
