# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpow.c

## Scope

Implements `double complex cpow`.

## APIs And Behavior

- Extracts exponent real/imaginary parts.
- If base magnitude is zero, returns complex zero.
- Computes `pow(|a|, x)`, phase `x*arg(a)`, and for nonzero imaginary exponent applies `exp(-y*arg(a))` and phase addition `y*log(|a|)`.
- Returns polar result `r*cos(theta) + i*r*sin(theta)`.

## Dependencies And Risks

- Simple polar formula; special-case coverage is limited.
- Zero base with complex exponent always returns zero.
