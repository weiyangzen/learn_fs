# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cosh.c

Implements legacy `cosh()` and `coshf()`. It uses different formulas for small, medium, and overflow-edge inputs.

Key behavior:
- Reduces to `|x|`; returns NaN unchanged on IEEE targets.
- For `x < 0.3465`, computes `1 + (exp(x)-1)^2/(2*exp(x))` using `__exp__E()`.
- For `0.3465 <= x <= 22`, computes `(exp(x) + 1/exp(x))/2`.
- Near overflow threshold, scales `exp((x-mln2hi)-mln2lo)` by `EXPMAX` to avoid unnecessary overflow.
- For large values, returns `exp(x)/2`.
- `coshf()` delegates to double `cosh()`.

Important dependencies: `../src/namespace.h`, `mathimpl.h`, `exp()`, `__exp__E()`, `scalb()`, and `copysign()`.

Notable risks:
- Threshold constants differ for VAX/Tahoe versus IEEE.
