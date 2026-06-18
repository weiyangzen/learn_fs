# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_clogl.c

Implements complex long-double logarithm `clogl(z)`, returning `log(|z|) + i*atan2(y,x)`. It uses special paths to avoid overflow, underflow, and accuracy loss near `|z| == 1`.

Key behavior: handles NaN/Inf through `logl(hypotl())`; uses `log1pl(ay*ay)/2` when real magnitude is 1; rescales extreme inputs; uses Dekker splitting and two-sum helpers for accurate squared-magnitude computation.

Important dependencies: `<complex.h>`, `fpmath.h`, `math_private.h`, `atan2l`, `hypotl`, `logl`, `log1pl`, `_2sum`, and `_2sumF`.

Notable risks: highly sensitive to long-double precision, exponent thresholds, and compensated summation details.
