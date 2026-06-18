# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cproj.c

## Scope

Implements `double complex cproj`, the C99 projection onto the Riemann sphere.

## APIs And Behavior

- If either component is infinite, sets real part to positive infinity / `HUGE_VAL` and imaginary part to signed zero with the sign of original imaginary part.
- Otherwise returns input unchanged.
- Uses `double_complex` layout macros.

## Dependencies And Risks

- Must preserve sign of imaginary zero for projected infinities.
