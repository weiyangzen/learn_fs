# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.c

Generated yacc parser for `eqn.y`.

Key behavior:
- Defines token constants, parse tables, token remapping, parser stack, error recovery, and reductions.
- Reductions invoke semantic layout functions for text, sums/products, fractions, marks, size/font changes, square roots, subscript/superscript, integrals, from/to, delimiters, diacritics, movement, piles, matrices, and columns.
- Preserves/restores yacc globals around `yyparse()`.
- Mirrors the grammar and actions from `eqn.y`.

Filesystem relevance:
- Generated parser logic only; no filesystem operations.
