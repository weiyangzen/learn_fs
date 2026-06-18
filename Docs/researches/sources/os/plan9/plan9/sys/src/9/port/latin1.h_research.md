# File Research: sources/os/plan9/plan9/sys/src/9/port/latin1.h

Purpose: Data table included by `latin1.c` to implement compose-key mappings.

Contents:
- Contains 100 table entries of lead sequence, selectable input characters, and corresponding rune string.
- Covers punctuation/math symbols, accented Latin letters, Greek letters, Cyrillic letters, fractions, chess/music symbols, currency symbols, arrows, set operators, and other Plan 9 compose mappings.

Dependencies and integration:
- Intended to be included inside `latintab[]`; it is not a standalone C header with guards.

Risks and notes:
- Entry order matters because `latin1.c` assumes prefixes appear earlier when one lead sequence prefixes another.
