# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_rewrt.c

`tl_rewrt.c` canonicalizes TL formula trees and normalizes negation.

Key responsibilities:
- Resets canonicalization state with `ini_rewrt`.
- Converts left-nested `AND`/`OR` trees into right-linked chains with `right_linked`.
- Recursively canonicalizes subtrees and stores/reuses canonical forms through cache with `canonical`.
- Pushes negation inward with `push_negation`, applying De Morgan rules, duality between `U` and `V`, double-negation elimination, and constant negation.
- Builds sorted canonical operand chains with `addcan`, using `DoDump` string forms for ordering and duplicate detection.
- Marks and removes redundant operands in `Canonical`.
- Simplifies boolean chains: removes `true` from conjunction, removes `false` from disjunction, collapses conjunctions containing `false`, disjunctions containing `true`, duplicate terms, and absorption cases.

Important interactions:
- `rewrite(n)` in `tl.h` composes `right_linked` and `canonical`.
- `tl_parse.c`, `tl_trans.c`, and `tl_buchi.c` rely on this normalization before equality/comparison.
- Uses `anywhere` and `isequal` from `tl_cache.c`.
