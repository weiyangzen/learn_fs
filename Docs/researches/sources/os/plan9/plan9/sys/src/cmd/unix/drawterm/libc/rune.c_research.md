# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rune.c

This file implements UTF-8/Rune conversion primitives.

Key behavior:
- `chartorune` decodes one UTF-8 sequence to a `Rune`.
- `runetochar` encodes one `Rune` as UTF-8.
- `runelen`, `runenlen`, and `fullrune` compute encoded lengths and completeness.

Important details:
- Uses Plan 9 constants such as `Runeself`, `Runeerror`, and `Runemax`.
- Rejects invalid encodings by returning `Runeerror`.
