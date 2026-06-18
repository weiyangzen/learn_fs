# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/util.c

Provides numeric parsing, angle formatting, angular distance, and gamma correction utilities for `scat`.

Key functions:
- `rint`, `rfloat`, and `sign` parse fixed-width numeric fields.
- `dangle` and `angle` convert between radians and milliarcsecond disk units.
- `hms`, `dms`, `ms`, `hm`, `hm5`, `dm`, and `deg` format angles.
- `getword`, `getra`, and related parsing helpers parse RA/Dec-style input.
- `xsqrt` clamps negative square-root inputs to zero.
- `dist` computes angular separation using spherical trig.
- `dogamma` maps pixel values through configured gamma/min/max settings to an 8-bit intensity.

Behavior notes:
- Defines global constants `PI_180`, `TWOPI`, and `LN2`.
- Formatting helpers use static buffers, so results are overwritten by subsequent calls.
- `dogamma` supports negative gamma display inversion through `gam.neg`.
