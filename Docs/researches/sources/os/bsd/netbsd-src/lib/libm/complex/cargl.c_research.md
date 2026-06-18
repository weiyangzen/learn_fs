# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cargl.c

## Scope

C99 `long double cargl(long double complex)` implementation.

## APIs And Behavior

- Returns `atan2l(cimagl(z), creall(z))`.

## Dependencies And Risks

- Delegates quadrant and signed-zero handling to `atan2l`.
