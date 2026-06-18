# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cargf.c

## Scope

C99 `float cargf(float complex)` implementation.

## APIs And Behavior

- Returns `atan2f(cimagf(z), crealf(z))`.

## Dependencies And Risks

- Delegates special values and signed zeros to `atan2f`.
