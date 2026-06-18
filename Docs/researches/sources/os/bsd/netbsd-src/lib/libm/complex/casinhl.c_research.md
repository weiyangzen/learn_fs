# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinhl.c

## Scope

Long-double inverse hyperbolic sine identity wrapper.

## APIs And Behavior

- Returns `-1.0L * I * casinl(z * I)`.

## Dependencies And Risks

- Depends on `casinl`.
