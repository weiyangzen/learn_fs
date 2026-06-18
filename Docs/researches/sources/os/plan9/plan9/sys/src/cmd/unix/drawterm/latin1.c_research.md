# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/latin1.c

This file implements Plan 9 compose-key translation for Latin-1 and extended runes.

Key behavior:
- Static `cvlist` table maps compose sequences to Unicode rune values.
- `unicode` accepts explicit hexadecimal Unicode entry.
- `latin1` resolves a sequence of runes to a composed rune or reports partial/no match.

Important details:
- The table supports accents, symbols, Greek, arrows, math, ligatures, and punctuation used by Plan 9 keyboard input.
- Return values distinguish complete match, partial prefix, and failure.
