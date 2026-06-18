# File Research: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabsf.c

## Scope

Compatibility wrapper for the historic `cabsf(struct complex)` ABI.

## APIs And Behavior

- Defines a local float-pair `struct complex`.
- Emits a link warning for compatibility `cabsf()`.
- Returns `hypotf(z.x, z.y)`.

## Dependencies And Risks

- Maintains old struct ABI, not C99 complex ABI.
