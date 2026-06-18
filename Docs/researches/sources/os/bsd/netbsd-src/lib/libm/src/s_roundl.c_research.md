# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_roundl.c

Implements long-double `roundl()` using `floorl()` and away-from-zero halfway handling.

Key behavior: returns nonfinite inputs unchanged, rounds positive values with `t - x <= -0.5`, and negative values via `floorl(-x)`.

Important dependencies: `namespace.h`, `<math.h>`, `isfinite`, and `floorl`.

Notable risks: only compiled under `__HAVE_LONG_DOUBLE`.
