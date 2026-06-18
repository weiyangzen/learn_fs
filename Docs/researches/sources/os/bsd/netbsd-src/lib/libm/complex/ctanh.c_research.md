# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanh.c

## Scope

Implements `double complex ctanh`.

## APIs And Behavior

- Denominator is `cosh(2x) + cos(2y)`.
- Returns `sinh(2x)/d + i*sin(2y)/d`.

## Dependencies And Risks

- Direct formula lacks near-cancellation helper unlike `ctan`.
