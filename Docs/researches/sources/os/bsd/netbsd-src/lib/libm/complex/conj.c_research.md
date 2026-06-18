# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/conj.c

## Scope

Implements `double complex conj`.

## APIs And Behavior

- Wraps input in `double_complex`.
- Negates `IMAG_PART(w)` and returns the complex value.

## Dependencies And Risks

- Preserves real part bitwise; imaginary sign handling uses normal unary negation.
