# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cprojl.c

## Scope

Implements `long double complex cprojl`.

## APIs And Behavior

- Uses `long_double_complex`.
- If real or imaginary part is infinite, real part becomes positive infinity and imaginary part becomes `copysignl(0.0L, cimagl(z))`.

## Dependencies And Risks

- Long-double infinity representation is abstracted by `<math.h>` / `HUGE_VAL`.
