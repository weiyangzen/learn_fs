# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos.c

Implements no-IEEE `sin`, `cos`, `sinf`, `cosf`, and long-double aliases.

Key behavior:
- Reduces arguments with `drem` into `[-pi, pi]`.
- Uses quadrant transforms around `pi/4`, `pi/2`, and `3pi/4`.
- Uses polynomial kernels `sin__S` and `cos__C` from `trig.h`.
- Returns NaN for NaN/infinity by `x - x`.
- Float functions delegate to double implementations.

This file owns the exported `__zero`, `__one`, `__half`, `__small`, and related constants by defining `_LIBM_DECLARE` before including `trig.h`.
