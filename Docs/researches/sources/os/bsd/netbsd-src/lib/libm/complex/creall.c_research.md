# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/creall.c

## Scope

Implements `long double creall(long double complex)`.

## APIs And Behavior

- Uses `long_double_complex` wrapper.
- Returns real component.

## Dependencies And Risks

- Depends on `math_private.h` long-double complex layout.
