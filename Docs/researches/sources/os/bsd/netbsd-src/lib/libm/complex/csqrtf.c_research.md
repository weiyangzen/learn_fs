# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrtf.c

## Scope

Implements `float complex csqrtf`.

## APIs And Behavior

- Mirrors `csqrt` with float constants.
- Special-cases real inputs with positive imaginary zero, pure imaginary inputs, and zero.
- Scales large inputs by `1/4` and small inputs by `2^26`, rescales by `2^-13`.

## Dependencies And Risks

- Depends on `cabsf`.
- Preserves branch-cut behavior around negative zero.
