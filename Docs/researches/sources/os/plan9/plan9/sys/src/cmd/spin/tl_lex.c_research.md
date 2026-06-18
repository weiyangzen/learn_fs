# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_lex.c

Lexer and symbol table for Spin LTL formulas.

Key responsibilities:
- Tokenizes LTL syntax from `tl_Getchar` input.
- Recognizes textual operators (`always`, `eventually`, `until`, `not`, optional `next`) and symbolic operators (`[]`, `<>`, `U`, `V`, `&&`, `||`, `->`, `<->`).
- Treats balanced `{...}` or `(...)` groups as predicates when they do not contain LTL operators.
- Interns predicate strings into a local `tl_lookup` symbol table.

Important functions:
- `tl_lex`/`tl_yylex`: main tokenization.
- `is_predicate`: peeks ahead to decide if parentheses/braces represent an atomic predicate.
- `read_upto_closing`: captures predicate text.
- `tl_follow`: validates two-character operators.
- `getsym`: copies a symbol wrapper while sharing the name.

Risks/quirks:
- Predicate lookahead has hard limits around 2047 chars and a 512-char local word buffer for operator detection.
- Whitespace handling expects tabs/newlines to be pre-normalized by `tl_main.c`.
