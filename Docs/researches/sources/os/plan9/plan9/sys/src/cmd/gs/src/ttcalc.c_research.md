# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.c

Purpose: FreeType-derived arithmetic helpers for TrueType fixed-point computations, with the instruction interpreter removed.

Key contents:
- Defines `Roots`, a lookup table used to seed square-root iteration.
- Implements `MulDiv` and `MulDiv_Round` using native 64-bit arithmetic when `LONG64` is available.
- Implements `Order64` and `Sqrt64` for native 64-bit mode.
- Provides software 64-bit implementation when native 64-bit is unavailable: `Neg64__`, `Add64`, `Sub64`, `MulTo64`, `Div64by32`, `Order64`, and `Sqrt64`.
- Keeps `Order32` and `Sqrt32` in disabled `#if 0` code.

Dependencies: `ttmisc.h`, `ttcalc.h`.

Integration notes: used by `ttfmain.c` for fixed-point transforms and scaling.

Risks: division by zero in software `Div64by32` saturates to signed limits; callers need to avoid invalid scale denominators where precise errors matter.
