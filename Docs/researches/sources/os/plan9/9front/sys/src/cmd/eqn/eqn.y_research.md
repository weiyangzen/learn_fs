# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/eqn.y

This yacc grammar defines the eqn language and maps parsed constructs to layout functions. It builds equation boxes and emits troff string-register definitions through semantic actions.

Key grammar features:
- A top-level equation is a sequence of boxes.
- Box constructs include quoted/contiguous text, spaces, sums/products/unions/intersections, fractions, marks, size/font/fat boxes, square roots, subscripts, superscripts, integrals, from/to limits, left/right delimiters, diacritics, moves, piles, and matrices.
- Matrix and pile grammars store intermediate boxes in the global `lp` stack.
- `LINEUP` and `MARK` support alignment across displayed equations.

Important implementation notes:
- Subscript/superscript grammar actions temporarily reduce `ps` by `deltaps`.
- Greater layout complexity lives in the operator files; the grammar mostly dispatches to those functions.
- `stuff` calls `putout` for successful equations and handles parse errors by warning.
