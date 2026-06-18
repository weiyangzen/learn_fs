# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conjf.c

## Scope

Implements `float complex conjf`.

## APIs And Behavior

- Uses `float_complex` wrapper and negates `IMAG_PART`.

## Dependencies And Risks

- Depends on `math_private.h`.
