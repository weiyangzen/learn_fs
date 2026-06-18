# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_pow.c

Implements no-IEEE `pow`, `powf`, and long-double aliases using K.C. Ng's algorithm with split-precision `log` and `exp`.

Key behavior:
- Handles special cases for zero exponent, exponent one/two/minus one, NaNs, infinities, signed zero, and negative bases.
- Uses `drem(y, 2)` to classify negative-base exponents as even integer, odd integer, or non-integer.
- Positive-base kernel `pow_P` computes `exp(y*log(x))` using `__log__D` and `__exp__D`.
- Splits `y` into truncated high/low parts before multiplying by the split log result.
- `powf` delegates to double `pow`.

Notable risks:
- Relies on old no-IEEE support routines such as `drem`, `finite`, and `copysign`.
- Uses pointer-based truncation macros on IEEE-style targets.
