# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cabsl.c

## Scope

C99 `long double cabsl(long double complex)` implementation.

## APIs And Behavior

- Extracts long-double real and imaginary parts.
- Returns `hypotl(real, imag)`.

## Dependencies And Risks

- Delegates all scaling and special handling to `hypotl`.
