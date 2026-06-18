# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j1.c

Implements Bessel functions `j1()` and `y1()` for order one, adapted from FDLIBM/SunPro code. It mirrors the structure of `n_j0.c` with order-one approximations and sign handling.

Key behavior:
- `j1()` is odd; it computes on `|x|` and restores sign.
- For tiny `x`, returns `0.5*x`; for `|x| < 2`, uses `x/2 + x*x^2*R/S`.
- For `|x| >= 2`, uses asymptotic sine/cosine combinations for `x - 3*pi/4` and helper functions `pone()`/`qone()`.
- `y1()` rejects `x <= 0`, handles infinities/NaNs, and for `x < 2` evaluates `x*U/V + (2/pi)*(j1(x)*log(x)-1/x)`.
- `pone()` and `qone()` select coefficient arrays by the same large-argument ranges as `n_j0.c`.

Important dependencies: `mathimpl.h`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `copysign()`, and `<float.h>`.

Notable risks:
- Special values vary by `_IEEE` mode.
- The asymptotic combination code is sensitive to cancellation and sign choices.
