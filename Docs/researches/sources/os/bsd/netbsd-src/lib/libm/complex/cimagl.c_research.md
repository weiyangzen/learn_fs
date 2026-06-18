# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimagl.c

## Scope

Implements `long double cimagl(long double complex)`.

## APIs And Behavior

- Uses `long_double_complex` wrapper from `math_private.h`.
- Returns the imaginary part as a real long double.

## Dependencies And Risks

- Depends on private long-double complex layout abstraction.
