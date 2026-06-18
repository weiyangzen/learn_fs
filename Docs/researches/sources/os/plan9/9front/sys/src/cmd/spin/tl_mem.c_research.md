# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_mem.c

`tl_mem.c` provides a small pooled allocator for the TL translator.

Key responsibilities:
- Allocates zeroed memory through `tl_emalloc`.
- Buckets small allocations by `union M` units in freelists, with gradually growing pool requests capped by `NOTOOBIG`.
- Allocates large blocks directly through the main `emalloc`.
- Tracks total allocated memory in `All_Mem`.
- Returns blocks to the freelist with `tfree`, validating an `A_USER` tag to catch double-free/free-corruption.
- Reports allocation statistics with `a_stats`.

Important interactions:
- Used by all TL node, graph, state, transition, and symbol allocations.
- Large allocations are intentionally not returned to the system; the free path logs them and leaves the actual `free(m)` commented out.
