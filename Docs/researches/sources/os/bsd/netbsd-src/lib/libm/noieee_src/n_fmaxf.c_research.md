# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmaxf.c

Implements float `fmaxf()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x > y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- Like `n_fmax.c`, NaN handling follows ordinary comparison behavior rather than full modern `fmaxf` semantics.
