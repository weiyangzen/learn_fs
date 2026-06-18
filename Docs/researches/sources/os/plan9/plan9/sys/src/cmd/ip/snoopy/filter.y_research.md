# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/filter.y

Yacc grammar and lexer for `snoopy` filter expressions.

Key behavior:
- Supports protocol words, field equality, inequality, grouping, negation, AND, and OR.
- Builds `Filter` AST nodes using `newfilter()`.
- Lexer splits on `!|&()= ` and recognizes `!=`, `&&`, and `||`.
- `yyinit()` sets the input filter string.
- `yyerror()` exits with a parse error.

Integration:
- `main.c` compiles and optimizes the resulting `filter` tree.

Risks and notes:
- Lexer delimiter list does not include tabs as token separators, though leading whitespace uses `isspace()`.
