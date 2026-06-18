# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cabs.c

Implements legacy `hypot()`, `cabs()`, and `z_abs()`. The main `hypot()` avoids overflow/underflow by comparing magnitudes and using Kahan-style formulas.

Key behavior:
- Normalizes `x` and `y` to nonnegative, swaps so `x >= y`, and handles zeros.
- If exponents differ enough, returns `x` while raising inexact.
- Uses different formulas for `x/y > 2` and `1 <= x/y <= 2`.
- Handles infinities and NaNs explicitly.
- `cabs(struct complex)` and `z_abs(struct complex *)` delegate to `hypot()`.

Important dependencies: `mathimpl.h`, `finite()`, `copysign()`, `logb()`, and `sqrt()`.

Notable risks:
- Uses old K&R-style function definitions for complex wrappers.
- A faster alternative `hypot()` is left under `#if 0`.
