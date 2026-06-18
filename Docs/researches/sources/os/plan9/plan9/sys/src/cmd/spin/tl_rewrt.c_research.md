# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_rewrt.c

Canonical rewrite engine for LTL formula ASTs.

Key responsibilities:
- Pushes negations inward using dualities.
- Right-links associative AND/OR trees.
- Sorts and deduplicates AND/OR clauses.
- Removes redundant clauses using boolean absorption and constants.

Important functions:
- `right_linked`: normalizes nested AND/OR associativity.
- `push_negation`: rewrites `!true`, `!false`, `!!p`, De Morgan forms, and U/V duals.
- `addcan`: builds a sorted canonical list based on `DoDump` string symbols.
- `Canonical`: canonicalizes top-level AND/OR, handles constants, duplicates, and absorption.

Data flow:
- Used via `rewrite(n)` macro across parser, cache, Buchi, and graph generation.
- Relies on `in_cache`/`cached` from `tl_cache.c` for repeated work.

Risks/quirks:
- Uses a single static `can` accumulator reset per call.
- Sorting key is a dumped symbolic representation, not a structural hash.
- Many operations mutate and release passed nodes.
