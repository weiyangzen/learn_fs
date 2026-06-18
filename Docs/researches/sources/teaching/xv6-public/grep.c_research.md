# File Research: sources/teaching/xv6-public/grep.c

User-space grep with a small regular expression matcher.

Behavior:
- Supports `^`, `.`, `*`, and `$`.
- Streams input into a 1024-byte buffer and processes complete newline-delimited lines.
- Runs against stdin or each named file.
- Uses Kernighan & Pike style `match`, `matchhere`, and `matchstar`.

Limitations:
- No character classes, alternation, escaping, or binary-file handling.
- Long lines are handled through leftover buffer shifting, but within simple buffer constraints.
