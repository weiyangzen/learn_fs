# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/util.c

Provides allocation, formatted string, warning, and ASCII-string-to-rune helpers for `htmlroff`.

Key points:
- `emalloc`, `erealloc`, `estrdup`, `erunestrdup`, `erunesmprint`, and `esmprint` fatal-exit on allocation failure.
- `warn` prints `htmlroff: <file>:<line>:` diagnostics using `%L`.
- `L` converts C string literals to cached `Rune*` strings and keys the cache by the literal pointer.
- The `L` cache allows source to use `L("name")` without manually constructing rune strings each time.

Dependencies and interactions:
- Used by all `htmlroff` modules.
- Depends on `linefmt` from `input.c` for warning locations.

Research relevance:
- This is common support code for the rune-oriented roff interpreter.
