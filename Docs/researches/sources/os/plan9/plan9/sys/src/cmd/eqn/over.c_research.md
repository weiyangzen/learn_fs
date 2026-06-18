# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/over.c

Fraction layout for `eqn`.

Key behavior:
- Builds a numerator-over-denominator box with tuned gap, bar width, and overline padding.
- Measures both sides, centers them around a temporary width register, draws the fraction line, and updates height/baseline.
- Frees denominator and temporary register.

Filesystem relevance:
- Typesetting layout only.
