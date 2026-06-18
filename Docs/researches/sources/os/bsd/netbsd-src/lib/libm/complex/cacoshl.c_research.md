# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshl.c

## Scope

Long-double inverse hyperbolic cosine wrapper source.

## APIs And Behavior

- Uses `clogl(z + csqrtl(z + 1) * csqrtl(z - 1))`.
- Disabled alternative notes `I * cacosl(z)` is not the principal value.

## Dependencies And Risks

- Depends on long-double `clogl` and `csqrtl`.
