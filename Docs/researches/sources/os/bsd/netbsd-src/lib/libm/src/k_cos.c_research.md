# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cos.c

This file implements the double cosine kernel `__kernel_cos(double x, double y)` for reduced arguments in approximately `[-pi/4, pi/4]`.

It evaluates a degree-14 cosine polynomial in `z = x*x`, incorporates the low-order tail `y` as `-x*y`, and uses a `qx` correction for larger reduced arguments to reduce cancellation in `1 - x*x/2`. Tiny inputs return 1 while triggering inexact when appropriate.

Dependencies are only `math_private.h` word macros and the local coefficient table.
