# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.c

Purpose: Generalized binary-floating-to-decimal formatter for arbitrary formats described by `FPI`.

Core behavior:
- `bitstob()` converts caller-supplied significand words into a `Bigint`.
- `gdtoa()` accepts an `FPI`, binary exponent, significand bits, result-kind flags, mode, and requested digits.
- Handles zero, finite, infinity, and NaN result kinds.
- Computes a decimal exponent estimate, tries a fast floating-point digit path where valid, and otherwise uses multiprecision arithmetic.
- Supports shortest, ecvt-style, fcvt-style, and debug modes.
- Tracks inexact direction by OR-ing `STRTOG_Inexlo` or `STRTOG_Inexhi` into `*kindp`.
- Handles directed rounding via `fpi->rounding`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses the shared `Bigint` helpers, `quorem`, powers-of-five scaling, and allocation helpers.
- Called by type-specific formatters such as `g_dfmt`, `g_ffmt`, `g_Qfmt`, `ldtoa`, and double-double formatting.
