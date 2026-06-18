# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/tuning.c

This file defines eqn layout tuning constants and default glyph/string definitions.

Key contents:
- Vertical spacing around sub/sup results.
- Diacritic shifts, bar dimensions, and height adjustments.
- Fat-box shift.
- Large operator sizing and baseline corrections.
- Integral sizing and limit offsets.
- Matrix spacing, fraction spacing, delimiter sizing, pile gaps, and sub/sup spacing.
- Default definitions for vec, dyad, hat, tilde, dot, dotdot, utilde, sum, union, intersection, product, and integral.
- `ftunetbl` support for user-tunable floating parameters.

Important implementation notes:
- `init_tune` installs string definitions into `deftbl` and tunable names into `ftunetbl`.
- `ftune` currently supports only `Subbase` and `Supshift`.
- `ftune` has no fallback if an unknown name reaches it, but callers only use names found in `ftunetbl`.
