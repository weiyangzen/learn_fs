# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/utf.c

Provides small UTF/rune helpers for libpanel text code.

Key behavior:
- `pl_idchar()` classifies identifier characters using whitespace/control/punctuation exclusions.
- `pl_rune1st()` detects the first byte of a UTF-8 rune.
- `pl_nextrune()` advances a char pointer to the next rune boundary.
- `pl_runewidth()` extracts one UTF-8 rune and returns its font width.

Important dependencies: Plan 9 UTF routines and font string measurement.

Notable risks:
- `pl_nextrune()` assumes valid UTF-8-like byte sequences and advances until a non-continuation byte.
