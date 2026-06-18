# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_cache.c

`tl_cache.c` implements formula-node allocation helpers, deep copy/release operations, formula equality checks, and a canonicalization cache for the LTL translator.

Key responsibilities:
- Initializes cache counters and list with `ini_cache`.
- Looks up prior canonicalization results with `in_cache` and stores new ones with `cached`.
- Reports cache stats with `cache_stats`.
- Allocates, shallow-copies, deep-copies, and releases `Node` trees with `tl_nn`, `getnode`, `dupnode`, and `releasenode`.
- Implements structural and associative/commutative equality through `sameform`, `sametrees`, `all_lfts`, `one_lft`, and `isequal`.
- Implements exact-shape match with `ismatch`.
- Searches formula trees for matching terms under `AND`/`OR` with `any_term`, `any_and`, `any_lor`, and `anywhere`.

Important interactions:
- `tl_rewrt.c` calls `cached`, `in_cache`, `isequal`, and `anywhere` during formula rewrite/canonicalization.
- `tl_buchi.c` uses `isequal` to detect identical transition conditions.
- Node memory comes from `tl_mem.c` and is returned through `tfree`.

Notable details:
- `isequal(NULL, TRUE)` treats missing conditions as true in some contexts.
- Canonicalization cache stores both the original and canonical tree, marking `same` when canonicalization did not change structure.
