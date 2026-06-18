# sources/storage-engines/wiredtiger/src/btree/row_srch.c

## Purpose

Implements row-store key search for WiredTiger btrees. It positions a `WT_CURSOR_BTREE` on the matching row-store key, the closest on-page key, or the appropriate update skiplist insertion point. The file is performance critical for reads and writes because ordinary cursor search, insert, append-like inserts, and page-instantiation paths all pass through this logic.

## Important APIs, Types, And Functions

`__wt_row_search` is the exported tree/leaf search routine. It accepts a cursor, search key, insert-mode flag, optional known leaf `WT_REF`, and leaf-safety flags, then fills cursor fields such as `ref`, `slot`, `ins_head`, `ins`, `compare`, `tmp`, and `WT_CBT_SEARCH_SMALLEST`.

`__wt_search_insert` searches a row-store insert skiplist and builds `cbt->ins_stack` and `cbt->next_stack` for later serialized insertion. `__search_insert_append` is an append fast path for insert lists, using the tail pointers to avoid a full skiplist walk when the new key is at or beyond the current last inserted key. `__validate_next_stack` is a diagnostic-only checker for skiplist search-stack ordering under `WT_CONN_DEBUG_STRESS_SKIPLIST`. `__check_leaf_key_range` validates that an optional leaf reference still covers the target key by comparing against the parent page index boundary keys.

The code depends on `WT_BTREE`, `WT_PAGE`, `WT_PAGE_INDEX`, `WT_REF`, `WT_ROW`, `WT_INSERT_HEAD`, `WT_INSERT`, `WT_ITEM`, `WT_COLLATOR`, cursor flags, row-page macros, and comparison helpers such as `__wt_compare`, `__wt_compare_skip`, `__wt_lex_compare_short`, and `__wt_lex_compare_skip`.

## Control Flow

When a caller supplies a leaf, `__wt_row_search` optionally checks the parent boundary keys, marks whether the leaf was found, and searches only that page. Otherwise it starts at `btree->root` and descends internal row pages. Each internal page search special-cases index 0 because reconciliation may store a non-application sentinel key there. The search uses three binary-search loops: no collator/short key, no collator/long key with skipped matching prefixes, and custom collator. Append-mode insertion first compares against the rightmost internal key and can descend directly to the rightmost child.

After choosing a child, the function handles split races with `__wt_split_descent_race` and `__wt_page_swap`; `WT_RESTART` releases the current page and restarts from the root. On the leaf, it performs the same three-way binary search over the row array. An exact row-array hit returns quickly. Otherwise it maps the search position to the smallest-key insert list or the insert list attached to the previous row slot, optionally tries the append insert-list path, and finally calls `__wt_search_insert`.

## State And Persistence Behavior

This file does not persist bytes itself; it constructs in-memory cursor position and insertion state over persisted row-page images and in-memory update skiplists. It may acquire and transfer page references into `cbt->ref`, release pages during restart/error handling, set append-history state (`cbt->append_tree`), and update `btree->maximum_depth`. Insert-list searches prepare stack pointers consumed by later update insertion code, so cursor state produced here directly affects durable logical updates written elsewhere.

## Dependencies And Integration Points

The implementation integrates with page management (`__wt_page_swap`, `__wt_page_release`), split detection, row-key decoding (`__wt_row_leaf_key`, `__wt_ref_key`), collation, skiplist update insertion, diagnostic flags, eviction read hints (`WT_CBT_READ_ONCE` to `WT_READ_WONT_NEED`), and caller-side cursor semantics expecting `cbt->tmp` to contain the exact found insert key on skiplist matches.

## Risks

The largest correctness risk is concurrent skiplist mutation. The code deliberately uses acquire barriers and single-read patterns so weakly ordered CPUs do not observe a higher-level skiplist insertion without the required lower-level insertion. Prefix-skip comparison is also subtle: it must reset per page and use safe match lengths or concurrent splits/inserts can cause wrong positioning. Internal-page slot 0 must never be passed to a collator. Split-race restarts must not leak or double-release page references. A wrong `compare` sign or `slot` choice would corrupt cursor positioning and insert placement.

## Test Signals

High-signal tests are row-store cursor search/insert/remove workloads with custom collators, long common-prefix keys, small keys, empty pages, smallest-key inserts, repeated append inserts, and concurrent insert/search stress on ARM or TSAN. The built-in diagnostic signal is `WT_CONN_DEBUG_STRESS_SKIPLIST`, which enables `__validate_next_stack`. Split-heavy workloads and tests that force `WT_RESTART` from `__wt_page_swap` are important for restart cleanup.
