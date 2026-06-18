# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fdim.c

Implements `fdim()`, `fdimf()`, and `fdiml()` through a macro template.

Key behavior: returns a NaN operand unchanged if either input is NaN; otherwise returns `x - y` when `x > y`, or `0.0`.

Important dependencies: `<math.h>` and `isnan`.

Notable risks: long-double behavior relies on compiler/library `isnan` support; overflow in `x-y` is intentionally not hidden.
