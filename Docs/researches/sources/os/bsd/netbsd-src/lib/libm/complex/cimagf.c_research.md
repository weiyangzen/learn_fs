# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimagf.c

## Scope

Implements `float cimagf(float complex)`.

## APIs And Behavior

- Uses `float_complex` wrapper and `IMAG_PART`.

## Dependencies And Risks

- Depends on `math_private.h` layout helpers.
