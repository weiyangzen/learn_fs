# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/hytab.c

Static hyphenation digram scoring tables for troff.

Key contents:
- Defines `Uchar`.
- Provides 26 by 13 packed scoring tables used by `n8.c`: `bxh`, `hxx`, `bxxh`, `xhx`, and `xxh`.

Important behavior:
- Scores are packed as two 4-bit values per byte for letter-pair lookup.
- `dilook()` in `n8.c` selects the high or low nibble based on the second letter.

Notable risks:
- The tables assume 26-letter ASCII alphabetic indexing.
- Values are opaque heuristic data; correctness depends on preserving exact bytes.
