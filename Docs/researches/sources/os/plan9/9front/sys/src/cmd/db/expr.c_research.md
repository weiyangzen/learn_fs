# File Research: sources/os/plan9/9front/sys/src/cmd/db/expr.c

Purpose: Expression parser and numeric/symbol token reader for `db`.

Key behavior:
- `expr()` parses left-associative dyadic expressions using `+`, `-`, `#` round-up, `*`, `%`, `&`, and `|`.
- `term()` handles monadic dereference from core (`*`), text/symbol map (`@`), negation, bitwise complement, and parenthesized expressions.
- `item()` parses symbols, local symbols, file:line references, numeric literals, dot/current function locals, ditto (`"`), next/previous dot, registers (`<reg`), and quoted character constants.
- `getnum()` supports decimal, octal, hex (`#` or `0x`), explicit decimal (`0t`), explicit octal (`0o`), and floating input coerced into `WORD`.
- `readsym()` and `readfname()` parse UTF-aware symbol and escaped filename tokens.
- `symchar()` and `convdig()` classify symbol/numeric characters.

Notable details:
- File references like `path:line` are detected before colon-command interpretation and converted through `file2pc()`.
- Local symbol lookup uses `localaddr()` against either a named function or the current function found from `mach->pc`.
