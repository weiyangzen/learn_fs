# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinl.c

## Scope

Implements `long double complex csinl`.

## APIs And Behavior

- Uses `_cchshl` for imaginary-part hyperbolic components.
- Returns `sinl(x)*ch + i*cosl(x)*sh`.

## Dependencies And Risks

- Depends on `cephes_subrl`.
