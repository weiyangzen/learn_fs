# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanhf.c

Implements float `atanhf()` using the same identity as `n_atanh.c`, but with `float`, `copysignf()`, and `log1pf()`.

Key behavior:
- Separates sign as `z = +/-0.5f`.
- Computes `x = |x|/(1-|x|)` and returns `z * log1pf(x+x)`.
- Keeps the VAX/Tahoe explicit `|x| == 1` path.

Important dependencies: `mathimpl.h`, `copysignf()`, and `log1pf()`.

Notable risks:
- Domain and NaN behavior are largely inherited from float arithmetic and `log1pf()`.
