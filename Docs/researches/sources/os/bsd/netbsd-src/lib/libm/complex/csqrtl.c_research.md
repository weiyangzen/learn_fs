# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtl.c

## Scope

Implements `long double complex csqrtl`, FreeBSD-derived with explicit special-case handling.

## APIs And Behavior

- Defines `THRESH = LDBL_MAX / (1 + sqrt(2))` to detect overflow risk.
- Handles zero, infinite imaginary part, NaN real part, and infinite real part before the normal path.
- Scales very large finite inputs by `1/4`, applies CACM Algorithm 312, then doubles the result if scaled.
- For nonnegative real part returns `t + i*b/(2t)`; for negative real part returns `|b|/(2t) + i*copysign(t,b)`.

## Dependencies And Risks

- Special cases compensate for incorrect compiler complex multiply/divide around infinities.
- Uses `z == 0.0L` complex comparison for zero.
