# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_j0.c

Implements Bessel functions `j0()` and `y0()` for order zero, adapted from early FDLIBM/SunPro code for non-IEEE support. It uses small-argument rational approximations and large-argument asymptotic expansions.

Key behavior:
- `j0()` is even; it reduces to `|x|`.
- For `|x| < 2`, `j0()` uses `1 - x^2/4 + x^4*R/S`.
- For `|x| >= 2`, it computes asymptotic forms using `sin(x)`, `cos(x)`, cancellation-avoidance identities, and helper approximations `pzero()`/`qzero()`.
- `y0()` rejects zero and negative inputs with infinity/NaN behavior, and for `x < 2` evaluates `U/V + (2/pi)*j0(x)*log(x)`.
- `pzero()` and `qzero()` select coefficient arrays by ranges `[2,2.857]`, `[2.857,4.545]`, `[4.545,8]`, and `[8,inf]`.

Important dependencies: `mathimpl.h`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `finite()`, and `<float.h>`.

Notable risks:
- IEEE versus VAX/Tahoe behavior is controlled by `_IEEE` and `infnan`.
- Very large-argument fast paths omit correction helpers to avoid overflow/cost.
