# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosh.c

## Scope

Implements `double complex ccosh`.

## APIs And Behavior

- Extracts `x = Re(z)`, `y = Im(z)`.
- Returns `cosh(x)*cos(y) + i*sinh(x)*sin(y)`.

## Dependencies And Risks

- Direct formula can inherit overflow behavior from `cosh` / `sinh`.
