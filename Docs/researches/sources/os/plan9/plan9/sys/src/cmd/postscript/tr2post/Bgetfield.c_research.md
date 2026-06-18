# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/Bgetfield.c

Purpose: Provides token/field parsing helpers over Plan 9 `Biobufhdr` streams for `tr2post`.

Key behavior:
- Defines local `isspace` for runes.
- `Bskipws` skips whitespace and updates `inputlineno` on newlines.
- `asc2dig` converts decimal/octal/hex digits.
- `Bgetfield` parses decimal ints, unsigned ints, strings, or single runes and ungets the first delimiter.

Dependencies and integration:
- Used throughout `tr2post` parsing: troff commands, device control commands, DESC files, metrics, and drawing arguments.

Risks and notes:
- The unsigned parser has likely bugs: it checks `*c` where `c` is an uninitialized local byte array, and computes `u = dig + (n * base)` instead of using `u`.
- Returns can conflate EOF and malformed fields in some paths.
- String parsing protects against overflow by requiring room for `UTFmax`.
