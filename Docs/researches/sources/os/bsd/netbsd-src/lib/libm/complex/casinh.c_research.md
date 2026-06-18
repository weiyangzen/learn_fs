# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinh.c

## Scope

Legacy standalone double complex inverse hyperbolic sine identity wrapper.

## APIs And Behavior

- Returns `-I * casin(z * I)`.

## Dependencies And Risks

- Inherits behavior from `casin`.
- Active build may use `catrig.c` for the double `casinh` symbol.
