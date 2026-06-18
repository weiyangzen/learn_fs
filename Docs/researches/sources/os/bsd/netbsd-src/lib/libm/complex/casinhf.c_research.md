# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinhf.c

## Scope

Legacy standalone float complex inverse hyperbolic sine wrapper.

## APIs And Behavior

- Returns `-I * casinf(z * I)` using float constants.

## Dependencies And Risks

- Inherits branch behavior from `casinf`.
