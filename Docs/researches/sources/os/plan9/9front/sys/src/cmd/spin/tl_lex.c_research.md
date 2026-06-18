# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_lex.c

`tl_lex.c` is the lexer and symbol table for standalone LTL formulas passed to the TL translator.

Key responsibilities:
- Tokenizes formula text from `tl_Getchar`, skipping spaces and returning `;` on end of input.
- Recognizes lowercase words for `true`, `false`, `always`, `eventually`, `until`, optional `next`, `c_expr`, `not`, or predicate names.
- Recognizes symbolic operators: `/\`, `\/`, `&&`, `||`, `[]`, `<>`, `<->`, `->`, `!`, `U`, `V`, and optional `X`.
- Treats parenthesized or braced non-temporal content as a single `PREDICATE`, using lookahead in `is_predicate` and extraction in `read_upto_closing`.
- Maintains a TL-specific symbol table through `tl_lookup`; clones symbols with `getsym`.

Important interactions:
- `tl_parse.c` consumes `tl_yylex`.
- Predicate recognition deliberately avoids swallowing nested temporal syntax.
- Uses main Spin `yytext` buffer and `isalnum_` helper from `spinlex.c`.
