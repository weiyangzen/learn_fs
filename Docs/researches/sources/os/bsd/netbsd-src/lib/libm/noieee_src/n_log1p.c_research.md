# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log1p.c

Implements no-IEEE `log1p`, `log1pf`, and long-double aliases using K.C. Ng's argument-reduction algorithm.

Key behavior:
- Reduces `1+x` into `2^k * (1+f)` and computes a correction term for lost low bits.
- Uses `s = f/(2+f)` and the shared `__log__L(s*s)` kernel.
- Splits `k*ln2` into `ln2hi` and `ln2lo` for accuracy.
- Handles `x == -1`, `x < -1`, NaN, and infinities with IEEE or VAX/Tahoe-specific signaling behavior.
- `log1pf` delegates to double `log1p`.
