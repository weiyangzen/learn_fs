# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_erfl.c

Implements Intel 80-bit `long double` `erfl()` and `erfcl()`, converted from Sun/FDLIBM-style double code. It uses interval-specific rational approximations for small, medium, and large magnitudes, with coefficients encoded through `LD80C()` unions from `math_private.h`.

Key behavior:
- Handles NaN and infinities directly: `erfl(+-inf)` returns `+-1`, and `erfcl(+-inf)` returns `0` or `2`.
- For `|x| < 0.84375`, evaluates `erf(x)` as `x + x*P(x^2)/Q(x^2)` and uses special tiny-input paths to avoid spurious underflow.
- For `0.84375 <= |x| < 1.25`, approximates around `erx`.
- For larger finite values, approximates `erfc` via asymptotic forms involving `exp(-x*x)` split with a float truncation of `ax`; `erfl()` saturates near `+-1` for `|x| >= 7`.
- `erfcl()` has an additional coefficient interval for `7 <= |x| < 108`, and underflows/rounds to `0` or `2` beyond that.

Important dependencies: `math.h`, `math_private.h`, `fabsl()`, `expl()`, `EXTRACT_LDBL80_WORDS`, `ENTERI`, `RETURNI`, and `LD80C`.

Notable risks:
- Accuracy depends on 80-bit representation and on the `math_private.h` ld80 word macros.
- Uses volatile `tiny` to force status flags and avoid compiler folding; removing it would change floating-point exception behavior.
