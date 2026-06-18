# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.c

LSP/LSF conversion implementation used for Vorbis floor0 spectral envelope reconstruction and LPC-to-LSP conversion.

Important routines:
- `vorbis_lsp_to_curve()` converts LSP values into a spectral floor curve. In this file both `FLOAT_LOOKUP` and `INT_LOOKUP` are explicitly undefined, so the active implementation is the simple non-optimized floating-point path.
- `cheby()` converts polynomial coefficients to Chebyshev form.
- `Laguerre_With_Deflation()` finds real roots with Laguerre iteration and deflation.
- `Newton_Raphson()` polishes roots after Laguerre.
- `vorbis_lpc_to_lsp()` converts LPC coefficients into LSP coefficients by forming symmetric/antisymmetric polynomials, finding roots, sorting them, and applying `acos()`.

Inactive code:
- Optimized float lookup and integer lookup implementations of `vorbis_lsp_to_curve()` are present under disabled macros and can include `lookup.c` directly.

Integration points:
- Declared in `lsp.h`.
- `floor0.c` calls `vorbis_lsp_to_curve()`.
- Uses `lookup.h` only for disabled optimized paths.

Risk and review signals:
- Several temporary arrays use plain `malloc()` without allocation checks.
- `Laguerre_With_Deflation()` mutates the `defl` pointer before calling `free(defl)`, which is suspicious because freeing an advanced pointer would be invalid if executed after pointer increment. This should be reviewed carefully.
- Root-finding failure returns `-1` for bad/complex roots, and `vorbis_lpc_to_lsp()` propagates failure.
- `vorbis_lsp_to_curve()` mutates the input `lsp` array as a documented side effect.

Filesystem relevance:
- No filesystem logic. It is audio codec math.
