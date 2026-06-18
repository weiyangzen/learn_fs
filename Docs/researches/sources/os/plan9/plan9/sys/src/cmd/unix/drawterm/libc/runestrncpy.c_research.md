# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncpy.c

This file copies a bounded number of runes.

Key behavior:
- `runestrncpy` copies up to `n` runes and pads with zeroes if source ends early.

Important details:
- Mirrors C `strncpy` semantics for `Rune`.
