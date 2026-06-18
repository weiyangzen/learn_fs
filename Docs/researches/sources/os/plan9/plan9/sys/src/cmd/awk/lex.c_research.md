# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/lex.c

Hand-written awk lexer.

It recognizes keywords, identifiers, numbers, strings, regex literals, comments, operators, redirections, field references, and balanced delimiters. Keywords are binary-searched from a sorted table and mapped to yacc tokens or built-in function subcodes.

Key behavior:

- Maintains `lineno`, `bracecnt`, `brackcnt`, and `parencnt`.
- Implements pushback with `unput()`/`unputstr()` and reads either inline `lexprog` or `-f` source via `pgetc()`.
- Handles awk string escapes including octal and hex.
- Uses `startreg()`/`regexpr()` so `/.../` is lexed as a regex only when grammar asks for one.
- Treats `$NF`, `$name`, `$expr`, and function args specially for indirect field references.
- Enforces safe mode for `system`.

It also records recent input in `ebuf`, which `lib.c` uses for syntax-error context printing.
