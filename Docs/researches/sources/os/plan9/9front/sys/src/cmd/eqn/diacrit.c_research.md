# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/diacrit.c

This file renders eqn diacritics over or under an existing box. Supported decorations include vector, dyad, hat, tilde, dot, double dot, bars, underbar, and under-tilde.

Key responsibilities:
- Allocates temporary string/register IDs with `salloc`.
- Computes vertical and horizontal shifts from box height, baseline, current point size, and tuning parameters.
- Emits troff strings for named diacritics from `deftbl` or constructs rule-based bars/underbars.
- Recomputes widths with `nrwid`.
- Appends the diacritic to the existing box string and updates box height where appropriate.

Important implementation notes:
- Italic boxes affect horizontal shift behavior.
- Underbar/utilde reset horizontal/vertical shifts differently from over-diacritics.
- Uses tuning globals such as `Dvshift`, `Dhshift`, `Barv`, `Barh`, `Ubarv`, and `Dheight`.
