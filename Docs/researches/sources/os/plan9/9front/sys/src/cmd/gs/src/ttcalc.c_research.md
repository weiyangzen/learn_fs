# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.c

FreeType-derived arithmetic routines for TrueType processing.

Key behavior:
- Provides a root-estimate lookup table used by square-root calculations.
- With native `LONG64`, implements:
  - `MulDiv`
  - `MulDiv_Round`
  - `Order64`
  - `Sqrt64`
- Without native 64-bit integers, implements manual 64-bit arithmetic:
  - `Neg64__`
  - `Add64`
  - `Sub64`
  - `MulTo64`
  - `Div64by32`
  - `Order64`
  - `Sqrt64`
- Handles signs explicitly and clamps divide overflow to signed 32-bit extrema.
- Contains unused `Order32`/`Sqrt32` under `#if 0`.

Dependencies and interactions:
- Includes `ttmisc.h` and `ttcalc.h`.
- Used by TrueType scaling, transforms, fixed-point multiplication/division, and outline construction.

Research relevance:
- Critical numeric substrate for fixed-point glyph transforms on platforms with or without native 64-bit arithmetic.
