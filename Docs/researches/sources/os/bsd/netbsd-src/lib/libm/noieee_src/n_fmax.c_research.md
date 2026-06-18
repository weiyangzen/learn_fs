# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_fmax.c

Implements double `fmax()` as a minimal comparison helper.

Key behavior:
- Returns `x` if `x > y`; otherwise returns `y`.
- Defines a weak alias from `fmaxl` to `fmax` where applicable.

Important dependencies: `<math.h>` and `<sys/cdefs.h>`.

Notable risks:
- This does not implement full modern `fmax` NaN preference semantics; behavior follows the raw comparison expression.
