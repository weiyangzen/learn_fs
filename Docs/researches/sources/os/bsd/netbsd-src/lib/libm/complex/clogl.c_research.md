# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/clogl.c

## Scope

Implements `long double complex clogl`.

## APIs And Behavior

- Uses `cabsl`, `logl`, and `atan2l`.
- Returns `log(|z|) + i*arg(z)`.

## Dependencies And Risks

- Direct composition of real long-double functions.
