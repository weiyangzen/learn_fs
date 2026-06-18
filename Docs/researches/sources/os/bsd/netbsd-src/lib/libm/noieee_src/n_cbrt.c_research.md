# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_cbrt.c

Implements IEEE-only `cbrt()`, plus `cbrtf()` and `cbrtl()` wrappers. It uses Kahan’s cube-root approximation with direct word manipulation and one Newton refinement.

Key behavior:
- Returns NaN/Inf and zero unchanged.
- Clears and later restores the sign bit.
- Builds a rough 5-bit cube-root approximation from exponent/mantissa words, with a subnormal path.
- Applies a rational refinement to about 23 bits, chops upward, then performs one Newton step to double precision.
- `cbrtf()` casts `cbrt()`, and `cbrtl()` calls double `cbrt()` when long double is not separately implemented.

Important dependencies: IEEE double layout and optional `national` word-order macro.

Notable risks:
- Violates modern strict-aliasing expectations by viewing doubles as `unsigned long *`.
- Only compiled for non-VAX/Tahoe targets.
