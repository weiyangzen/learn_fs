# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j0f.c

Implements fdlibm kernels `__ieee754_j0f(float)` and `__ieee754_y0f(float)`.

Key behavior:
- Float version of `e_j0.c`.
- Uses float polynomial/rational approximations for small inputs and asymptotic helper functions for `x >= 2`.
- `y0f` handles NaN/infinity, zero, negative input, tiny positive input, and ordinary positive input.
- Helper functions `pzerof` and `qzerof` select range-specific coefficient tables.
- Some extremely-large shortcuts are inside `DEAD_CODE` blocks and are not active.
