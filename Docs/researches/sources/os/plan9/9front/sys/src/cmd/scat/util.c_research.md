# File Research: sources/os/plan9/9front/sys/src/cmd/scat/util.c

Purpose: Utility functions for angles, formatting, parsing, distance, and gamma mapping in `scat`.

Key routines:
- Constants: `PI_180`, `TWOPI`, `LN2`.
- `dangle`/`angle`: convert between radians and milliarcsecond disk angles.
- `hms`, `dms`, `ms`, `hm`, `hm5`, `dm`, `deg`: angle formatters.
- `getword`: parses lowercased header words and quoted strings.
- `getra`: parses mixed-unit RA/Dec angle strings.
- `dist`: angular distance on the sphere.
- `dogamma`: maps pixel intensity through configured gamma and inversion.

Integration: Used throughout `scat` for catalog parsing, display output, DSS image contrast, and coordinate math.

Risks:
- Most formatters return static buffers, so multiple calls in one expression can overwrite earlier results.
- `getra` accepts both RA-style and degree-style units, relying on caller context.
