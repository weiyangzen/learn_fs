# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccosf.c

## Scope

Implements `float complex ccosf`.

## APIs And Behavior

- Uses `_cchshf` and float trig functions.
- Returns `cosf(x)*ch - i*sinf(x)*sh`.

## Dependencies And Risks

- Depends on `cephes_subrf`.
