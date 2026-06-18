# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/regx.c

This file implements Acme’s regular expression compiler and forward/backward NFA executor.

Key behavior:
- `rxinit()` initializes the compile channel and empty last regexp.
- `rxcompile()` compiles a null-terminated rune regexp into both forward and backward programs, caching the last regexp.
- Parser supports literals, escapes, `.`, `^`, `$`, `[]`, `[^]`, grouping, alternation, concatenation, `*`, `+`, and `?`.
- `rxexecute()` runs the forward machine over either `Text` or rune string input.
- `rxbexecute()` runs the backward machine over `Text`.
- Captures are stored in `Rangeset` slots up to `NRange`.

Important details:
- Program size is fixed at `NPROG`.
- Active NFA list size is fixed at `NLIST`; overflow warns and fails.
- Backward compilation reverses concatenation where needed.
- Character classes support ranges and escaped `\n`.
- `lastregexp` supports empty regexp reuse elsewhere.

Filesystem relevance:
- Indirect: powers address searches and edit commands across file-backed buffers.
