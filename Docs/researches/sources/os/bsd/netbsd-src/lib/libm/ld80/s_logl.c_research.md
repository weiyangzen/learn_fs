# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_logl.c

Implements Intel 80-bit `logl()`, `log1pl()`, `log10l()`, and `log2l()`. The core algorithm decomposes the argument into `X * 2^k`, selects one of 128 centered intervals for `X`, uses tabulated reciprocal/log pieces, and evaluates a minimax polynomial for `log(1+d)`.

Key behavior:
- The main kernel `k_logl()` returns either a single high result or a high/low pair through `struct ld` when structure return is enabled.
- Handles zero, negative values, subnormals, infinities, NaNs, pseudo-infinities, pseudo-NaNs, and unnornals via ld80 word inspection.
- Uses tables `T[]` for reciprocal and split log constants; optionally uses `U[]` to compute reduced `d` with exact correction terms.
- `log1pl()` forms `1+x` as a high/low decomposition, preserving precision for small `x` and rejecting `x <= -1` correctly.
- `log10l()` and `log2l()` reuse `k_logl()` and multiply the high/low natural-log result by split reciprocal constants.

Important dependencies: `math_private.h`, ld80 extraction/insertion macros, `_2sumF`, `_3sumF`, `ENTERI`, `RETURNI`, and optional debug `fenv.h`.

Notable risks:
- The file is heavily tied to Intel 80-bit encoding and to exact cancellation properties in the tables.
- The `STRUCT_RETURN` path is selected through macros and affects how `logl()` shares work with `log10l()` and `log2l()`.
- Comments note difficult rounding-mode and underflow subtleties; table edits would require numerical revalidation.
