# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.h

Compose table data included into `latin1.c`.

Key contents:
- Defines initializer rows mapping compose leaders and final character sets to output rune strings.
- Covers accented Latin letters, Greek, Cyrillic, math symbols, arrows, fractions, punctuation, currency, chess symbols, Hebrew-like/private symbols, and other Plan 9 compose sequences.
- Includes both one-character leaders and two-character leader prefixes.

Role:
- Data source for `latin1()`; each row maps `ld` plus a selected character in `si` to the corresponding rune at the same offset in `so`.

Risks:
- This is included as raw initializer rows, not a standalone header with guards.
- Sequence validity and “need more input” behavior depend on row order.
