# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sincos1.c

Implements convenience wrappers `sincos` and `sincosf`.

Key behavior:
- `sincos(double x, double *s, double *c)` stores `sin(x)` and `cos(x)`.
- `sincosf(float x, float *s, float *c)` stores `sinf(x)` and `cosf(x)`.
- When long double is unavailable, `sincosl` aliases to `sincos`.

There is no shared argument reduction; this file intentionally delegates to existing sine/cosine functions.
