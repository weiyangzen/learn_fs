# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanh.c

## Scope

Legacy standalone double complex inverse hyperbolic tangent wrapper.

## APIs And Behavior

- Returns `-I * catan(z * I)`.

## Dependencies And Risks

- Inherits singularity and overflow behavior from `catan`.
