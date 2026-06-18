# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosl.c

## Scope

Implements `long double complex ccosl`.

## APIs And Behavior

- Uses `_cchshl` for hyperbolic parts.
- Returns `cosl(x)*ch - i*sinl(x)*sh`.

## Dependencies And Risks

- Depends on `cephes_subrl`.
