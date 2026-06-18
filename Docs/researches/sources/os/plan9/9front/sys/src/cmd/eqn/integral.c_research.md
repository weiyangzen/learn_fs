# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/integral.c

This file creates integral symbols and attaches optional subscript/superscript limits.

Key responsibilities:
- `setintegral` allocates a box containing the predefined integral glyph from `deftbl`.
- Sets integral height, baseline, and roman font metadata from tuning parameters.
- `integral` positions lower and/or upper limit boxes around the integral symbol.
- Delegates combined limit layout to `shift2` or `bshiftb`.

Important implementation notes:
- Lower and upper limits are shifted by separate horizontal/vertical tuning values (`Int1h`, `Int1v`, `Int2h`, `Int2v`) before being attached.
- Integral handling reuses the same sub/sup machinery used for ordinary boxes.
