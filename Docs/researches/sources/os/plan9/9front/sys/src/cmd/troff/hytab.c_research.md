# File Research: sources/os/plan9/9front/sys/src/cmd/troff/hytab.c

Read completely: 126 lines, 7232 bytes.

Static hyphenation digram tables for legacy troff/nroff hyphenation. It defines unsigned-char matrices such as `bxh`, `hxx`, `bxxh`, `xhx`, and `xxh`, used by `n8.c` scoring logic.

Key behavior:
- Contains no functions; it is data-only.
- Tables encode pair/trigram-like hyphenation desirability values for alphabetic contexts.

Dependencies:
- Used by `dilook`/`digram` style hyphenation logic in `n8.c`.

Reliability notes:
- The tables are opaque historical data; changing values would directly affect line breaking and hyphen insertion.
