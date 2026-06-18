# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosl.h

This header defines inline long-double `__kernel_sincosl(long double x, long double y, int iy, long double *sn, long double *cs)` for reduced arguments.

It has separate coefficient sets for ld80 (`LDBL_MANT_DIG == 64`) and ld128 (`LDBL_MANT_DIG == 113`). The function evaluates sine and cosine polynomials, incorporates the low-order argument tail `y`, and stores both outputs. The ld128 path uses higher-degree sine and cosine terms, with some trailing coefficients stored as double.

Unsupported long-double formats are rejected at compile time.
