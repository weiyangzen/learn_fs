# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_expl.c

Implements Intel 80-bit `expl()` and `expm1l()`. `expl()` delegates core argument reduction and table/polynomial evaluation to `__k_expl()` from `k_expl.h`; `expm1l()` has its own careful small- and medium-range logic to preserve cancellation-sensitive accuracy.

Key behavior:
- `expl()` filters exceptional inputs, uses `__k_expl(x, &hi, &lo, &k)`, sums the high/low result, and scales by `2^k`.
- Overflow and underflow thresholds are encoded as ld80 constants rounded toward zero.
- `expm1l()` uses a direct Taylor/minimax path for roughly `[-0.1659, 0.1659]`.
- Outside that small interval, `expm1l()` reduces by table intervals from `k_expl.h`, evaluates lower terms, and handles special `k == 0`, `k == -1`, large positive `k`, and negative `k` cases to avoid cancellation.

Important dependencies: `math_private.h`, `k_expl.h`, `fabsl()`, `rnintl()`, `irint()`, `SUM2P`, `ENTERI`, and `RETURNI/RETURNF`.

Notable risks:
- Correctness relies on the shared `k_expl.h` constants, interval count, and polynomial coefficients.
- Several branches are specifically tuned for floating-point exception and rounding behavior; simple algebraic simplification would be unsafe.
