# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosl.c

## Scope

Long-double complex arccosine wrapper source.

## APIs And Behavior

- Includes `cephes_subrl.h` for long-double constants.
- Computes `w = casinl(z)` and returns `(M_PI_2L - creall(w)) - cimagl(w) * I`.

## Dependencies And Risks

- Depends on `casinl` and long-double constants.
