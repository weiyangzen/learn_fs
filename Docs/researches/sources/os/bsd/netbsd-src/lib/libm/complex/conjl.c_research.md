# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conjl.c

## Scope

Implements `long double complex conjl`.

## APIs And Behavior

- Uses `long_double_complex` wrapper.
- Negates imaginary component and returns the result.

## Dependencies And Risks

- Uses private layout helper to avoid compiler-specific complex access issues.
