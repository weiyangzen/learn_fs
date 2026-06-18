# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmin.c

Implements double `fmin()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x < y`; otherwise returns `y`.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- NaN and signed-zero behavior follow the comparison expression, not a fully specified modern implementation.
