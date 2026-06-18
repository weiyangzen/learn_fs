# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacosh.c

## Scope

Legacy standalone double complex inverse hyperbolic cosine implementation.

## APIs And Behavior

- Disabled code notes `I * cacos(z)` does not give the principal value.
- Active formula returns `clog(z + csqrt(z + 1) * csqrt(z - 1))`.

## Dependencies And Risks

- Depends on `clog` and `csqrt`.
- Principal-value correctness depends on the square-root branch behavior.
