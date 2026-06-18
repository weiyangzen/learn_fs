# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/diacrit.c

Builds eqn boxes with accents and bars.

Key behavior:
- Adds vector, dyad, hat, tilde, dot, double-dot, bar, high/low bar, underbar, and utilde decorations to an existing box.
- Computes vertical and horizontal shifts from tuning parameters and current point size.
- Uses temporary string/number registers, width measurements, and troff motion commands.
- Updates box height for above-text accents and adjusts classes/fonts.

Filesystem relevance:
- Typesetting module only; no filesystem behavior.
