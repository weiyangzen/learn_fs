# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanhl.c

## Scope

Long-double inverse hyperbolic tangent identity wrapper.

## APIs And Behavior

- Returns `-1.0L * I * catanl(z * I)`.

## Dependencies And Risks

- Depends on `catanl`.
