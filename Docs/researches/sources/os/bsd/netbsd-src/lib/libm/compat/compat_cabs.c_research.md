# File Research: sources/os/bsd/netbsd-src/lib/libm/compat/compat_cabs.c

## Scope

Compatibility wrapper for the historic pre-C99 `cabs(struct complex)` ABI.

## APIs And Behavior

- Defines a local `struct complex { double x; double y; }`.
- Emits a link warning for references to compatibility `cabs()`.
- Returns `hypot(z.x, z.y)`.

## Dependencies And Risks

- Separate from C99 `double complex cabs(double complex)`.
- ABI depends on the old struct-by-value layout.
