# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cabs.c

## Scope

C99 `double cabs(double complex)` implementation.

## APIs And Behavior

- Extracts real and imaginary parts via GNU complex extensions.
- Returns `hypot(real, imag)`.

## Dependencies And Risks

- Relies on `hypot` for scaling and special-value behavior.
