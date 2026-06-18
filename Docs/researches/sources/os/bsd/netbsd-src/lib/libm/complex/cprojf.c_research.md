# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cprojf.c

## Scope

Implements `float complex cprojf`.

## APIs And Behavior

- Projects complex infinities to positive real infinity plus signed zero imaginary part.
- Returns finite inputs unchanged.

## Dependencies And Risks

- Uses `float_complex` and `copysignf`.
