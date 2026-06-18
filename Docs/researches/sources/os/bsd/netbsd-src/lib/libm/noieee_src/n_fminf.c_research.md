# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fminf.c

Implements float `fminf()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x < y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- NaN and signed-zero behavior follow ordinary comparison behavior.
