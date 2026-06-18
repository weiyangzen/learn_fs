# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexp.c

## Scope

Implements `double complex cexp`.

## APIs And Behavior

- Computes `r = exp(Re(z))`.
- Returns `r*cos(Im(z)) + i*r*sin(Im(z))`.

## Dependencies And Risks

- Direct formula inherits overflow/underflow from `exp`.
