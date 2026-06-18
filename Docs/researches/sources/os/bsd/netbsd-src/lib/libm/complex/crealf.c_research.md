# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/crealf.c

## Scope

Implements `float crealf(float complex)`.

## APIs And Behavior

- Uses `float_complex` and returns `REAL_PART`.

## Dependencies And Risks

- Depends on private complex layout helpers.
