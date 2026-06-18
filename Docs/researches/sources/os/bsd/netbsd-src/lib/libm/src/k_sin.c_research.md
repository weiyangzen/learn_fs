# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sin.c

This file implements the double sine kernel `__kernel_sin(double x, double y, int iy)` for reduced arguments.

It uses an odd polynomial approximation for `sin(x)/x` on `[-pi/4, pi/4]`. If `iy == 0`, it evaluates `sin(x)` directly; otherwise it incorporates the low-order tail `y` from range reduction using a compensated formula for `sin(x+y)`.

Tiny inputs return `x` with inexact behavior. Dependencies are local coefficients and double high-word extraction.
