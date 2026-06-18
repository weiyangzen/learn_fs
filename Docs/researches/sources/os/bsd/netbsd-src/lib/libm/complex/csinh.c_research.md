# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinh.c

## Scope

Implements `double complex csinh`.

## APIs And Behavior

- Returns `sinh(x)*cos(y) + i*cosh(x)*sin(y)`.

## Dependencies And Risks

- Direct formula inherits overflow behavior from real hyperbolic functions.
