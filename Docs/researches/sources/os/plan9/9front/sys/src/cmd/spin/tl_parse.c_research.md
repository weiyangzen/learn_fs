# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_parse.c

`tl_parse.c` is the recursive-descent parser and algebraic simplifier for TL formulas.

Key responsibilities:
- Parses factors: parentheses, negation, `[]`, `<>`, optional `X`, `c_expr`, predicates, true, and false.
- Parses binary operators by precedence with `tl_level`: temporal `U`/`V`, then boolean `OR`/`AND`/`IMPLIES`/`EQUIV`.
- Performs early simplifications in `tl_factor` and `bin_simpler`, including idempotence, constants, nested eventually/always, implication elimination, equivalence expansion, and several LTL absorption/distribution identities.
- Pushes negations down with `push_negation`.
- Calls `rewrite` to canonicalize simplified subtrees.
- Entrypoint `tl_parse` parses a formula, validates trailing input, and calls `trans`.

Important interactions:
- Consumes tokens from `tl_lex.c`.
- Builds nodes with `tl_nn`, compares with `isequal`, and invokes rewrite/cache logic.
- Hands the final formula tree to `tl_trans.c`.

Notable details:
- Optimization blocks are guarded by `NO_OPT`.
- Optional `NXT` support adds `NEXT` simplifications when compiled in.
