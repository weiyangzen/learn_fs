# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinf.c

## Scope

Implements `float complex csinf`.

## APIs And Behavior

- Uses `_cchshf` and float trig functions.
- Returns `sinf(x)*ch + i*cosf(x)*sh`.

## Dependencies And Risks

- Depends on `cephes_subrf`.
