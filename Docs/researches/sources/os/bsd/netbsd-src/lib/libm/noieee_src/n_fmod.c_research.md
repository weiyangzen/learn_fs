# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmod.c

Implements legacy `fmod()` and `fmodf()`. It computes the floating-point remainder by repeated scaled subtraction based on exponents.

Key behavior:
- Rejects zero divisor, NaN divisor, and nonfinite dividend on IEEE targets by returning invalid NaN expression.
- Works with absolute values of `x` and `y`, preserving the original sign of `x` at return.
- Uses `frexp()` to compare exponents and `ldexp()` to align the divisor before subtracting.
- Loops until the remainder magnitude is below the divisor.
- `fmodf()` delegates to double `fmod()`.

Important dependencies: `mathimpl.h`, `fabs()`, `frexp()`, `ldexp()`, `isnan()`, and `finite()`.

Notable risks:
- The repeated subtraction loop can be slow for hostile exponent/mantissa combinations.
- Test harness code remains under `TEST_FMOD`.
