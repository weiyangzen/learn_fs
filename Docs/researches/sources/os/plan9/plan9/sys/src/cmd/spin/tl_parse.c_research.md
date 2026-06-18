# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_parse.c

Recursive-descent parser and local simplifier for LTL formulas.

Key responsibilities:
- Parses unary temporal/logical operators, predicates, booleans, parentheses, and two binary precedence levels.
- Performs algebraic simplifications during parsing for U/V/AND/OR/IMPLIES/EQUIV and optional NEXT.
- Converts implication/equivalence into primitive forms.
- Sends final AST to `trans`.

Important functions:
- `tl_factor`: parses atomic/unary expressions, expands `[]p` to `false V p` and `<>p` to `true U p`.
- `bin_simpler`: simplifies binary forms such as `p U p`, identity/absorbing boolean rules, and some temporal absorption rules.
- `tl_level`: precedence parser over `U/V` and `OR/AND/IMPLIES/EQUIV`.
- `tl_parse`: parse, verify no trailing input, call `trans`.

Risks/quirks:
- Associativity and simplification rely on mutable AST reuse.
- Optional `NO_OPT` disables many simplifications.
- Parser uses global `tl_yychar` and `tl_yylval`.
