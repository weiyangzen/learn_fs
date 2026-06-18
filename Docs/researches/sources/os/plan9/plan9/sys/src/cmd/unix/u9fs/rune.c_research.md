# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/rune.c

- Role: Implements Plan 9 UTF/Rune conversion helpers for the Unix port.
- Key functions: `chartorune`, `runetochar`, `runelen`, and `utflen`.
- Behavior: Validates UTF encodings, rejects overlong forms and surrogate halves, maps bad input to `Runeerror`.
- Integration: Used by argument parsing, formatting, tokenization, and UTF-aware string search.
- Risks/notes: `plan9.h` defines `UTFmax` as 3 and `Rune` as `ushort`, so 4-byte Unicode support is effectively disabled in this build profile.
