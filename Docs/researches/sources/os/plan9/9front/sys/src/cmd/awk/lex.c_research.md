# File Research: sources/os/plan9/9front/sys/src/cmd/awk/lex.c

Implements the awk lexical scanner.

Key responsibilities:
- Tokenizes identifiers, keywords, numbers, strings, regular expressions, operators, braces, comments, and line continuations.
- Maintains `lineno`, brace/bracket/paren counts, pushback buffer, and error context buffer.
- Binary-searches sorted keyword table for awk keywords and builtins.
- Handles argument names inside function bodies.
- Parses string escapes including common escapes, octal, and hex.
- Supports `$` field references and indirect expressions.
- Provides `startreg`/`regexpr` for grammar-directed regex literal scanning.
- Reads lexical input either from inline program string or `pgetc()` program files.

Important interfaces:
- Exports `yylex`, `input`, `unput`, `unputstr`, `startreg`.
- Uses `setsymtab`, `tostring`, `to_number`, `adjbuf`, and parser token definitions from `y.tab.h`.

Notes:
- `sc` returns a synthetic semicolon before a closing brace, then returns `}` on the next scan.
- `safe` rejects `system`.
