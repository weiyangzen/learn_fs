# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/Bgetfield.c

Field scanner helpers for `tr2post`. It defines a local whitespace predicate, skips whitespace while tracking `inputlineno`, converts ASCII digits for bases 8/10/16, and implements `Bgetfield` for decimal ints, unsigned ints, strings, and runes.

Integration points:
- Used throughout `tr2post` parsing: DESC/font tables, troff command stream, picture/device-control args.
- Relies on Plan 9 `Bgetrune`, `Bungetrune`, and rune conversion functions.

Risks:
- The unsigned case checks `*c` even though `c` is an uninitialized local byte buffer, and accumulates `u = dig + (n * base)` instead of using `u`; this looks like a real parsing bug.
- Numeric parsing returns `-1` on EOF even after partial data in some paths.
- Local `isspace(Rune)` shadows libc-style names.
