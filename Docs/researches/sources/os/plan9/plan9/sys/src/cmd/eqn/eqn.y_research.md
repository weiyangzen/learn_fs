# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.y

Yacc grammar for `eqn`.

Key behavior:
- Defines tokens and precedence for equation constructs.
- Grammar parses equation sequences, grouping, quoted/contiguous text, spaces, special operators, fractions, marks, font/size changes, square roots, sub/superscripts, integrals, from/to limits, left/right delimiters, diacritics, movement, piles, matrices, and column lists.
- Semantic actions call the corresponding box-building functions.
- Adjusts point size around scripts/limits with `deltaps`.

Filesystem relevance:
- Grammar source only; no filesystem operations.
