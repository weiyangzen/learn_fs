# sources/storage-engines/wiredtiger/src/btree/bt_npos.c

Purpose: computes and consumes approximate normalized page positions in a B-tree. Normalized positions are doubles in `[0, 1]` used mainly by eviction to resume tree walks without holding hazard pointers too long, and by read paths to seek near a fractional point in a dataset.

Important APIs/types/functions: `__wt_page_npos` computes a page's normalized position and optional path string. `__wt_page_from_npos` finds a page near a normalized position. Convenience wrappers `__wt_page_from_npos_for_eviction` and `__wt_page_from_npos_for_read` add the right read/walk flags. Static helpers `__page_from_npos_internal` and `__find_closest_leaf` implement descent and leaf cleanup.

Control flow: position calculation starts with a caller-provided intra-page `start` value, enters the page-index generation, ascends through parent refs, and folds each `(slot + npos) / entries` into a root-relative position, clamping the result. Lookup starts at the root under page-index protection, repeatedly multiplies the local fraction by child count to choose a child index, then either descends with `__wt_page_swap` or stops early depending on ref state and flags. Eviction mode never reads disk pages; read mode may wait/restart on locked refs unless `WT_READ_NO_WAIT` is set. After the internal descent, `__find_closest_leaf` tree-walks to a suitable leaf if the initial result is internal, deleted, or otherwise unsuitable.

State and persistence behavior: no disk state is changed. Runtime effects are hazard/page references acquired and released during page swaps and walks, stats increments distinguishing eviction/read max-walk cases, and optional diagnostic path-string output. Returned positions are approximate and can shift after splits.

Dependencies and integration points: integrates with eviction walk state, tree walk flags, hazard pointer/page-swap machinery, page-index generations, ref parent/index lookup, and stats. It relies on balanced-tree assumptions only for quality, not for safety.

Risks: precision is approximate, especially in unbalanced in-memory trees or after splits; callers must tolerate skipped or repeated pages. Eviction-specific behavior may return `NULL` when the root would otherwise be returned, signaling restart/end. Incorrect flag combinations could load pages during eviction or wait in contexts that need no-wait behavior. Path string writing depends on caller-provided buffer length.

Test signals: round-trip a page through `__wt_page_npos(..., 0.5)` and `__wt_page_from_npos`, boundary values below 0 and above 1, forward/backward adjacent-page iteration via out-of-range starts, eviction mode with disk/locked/deleted refs, read mode restart on splits, path string formatting, and stats for read versus eviction walks.
