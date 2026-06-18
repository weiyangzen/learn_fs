# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosf.c

## Scope

Legacy standalone float complex arccosine implementation.

## APIs And Behavior

- Computes `casinf(z)`.
- Returns `((float)M_PI_2 - crealf(w)) - cimagf(w) * I`.

## Dependencies And Risks

- Inherits branch-cut and special-case behavior from `casinf`.
- Build may use `catrigf.c` for the float arccosine symbol.
