# File Research: sources/os/linux/linux/fs/ubifs/lprops.c

## Purpose

`lprops.c` maintains UBIFS LEB properties and their fast lookup categories. Each main-area LEB has free, dirty, flags, category, and heap/list position state. The file keeps category heaps/lists coherent, updates global space accounting, exposes quick find helpers, and contains debug scanners that verify lprops against actual flash contents and the TNC.

## Categories and Heaps

LEBs are categorized as dirty, dirty index, free, uncategorized, empty, freeable, or freeable dirty index. `ubifs_categorize_lprops()` implements the rules. Taken LEBs become uncategorized. Fully free LEBs are empty. LEBs whose free plus dirty equals the LEB size are freeable, with index LEBs going to `LPROPS_FRDI_IDX`. Index LEBs with enough reclaimable space for an index node go to `LPROPS_DIRTY_IDX`; data LEBs with meaningful dirty space go to `LPROPS_DIRTY`, and those with free space go to `LPROPS_FREE`.

The dirty, dirty-index, and free categories are heaps. `get_heap_comp_val()` chooses the comparison metric: free bytes for free LEBs, free plus dirty for dirty index LEBs, and dirty bytes otherwise. `move_up_lpt_heap()`, `adjust_lpt_heap()`, `add_to_lpt_heap()`, and `remove_from_lpt_heap()` implement max-heap maintenance. If a heap is full, `add_to_lpt_heap()` may evict a weaker bottom-half entry to the uncategorized list.

List categories are maintained by `ubifs_add_to_cat()`, `ubifs_remove_from_cat()`, `ubifs_replace_cat()`, and `ubifs_ensure_cat()`. Replacement supports LPT copy-on-write during commit, where pnodes and their embedded lprops can be copied and all category references must be redirected.

## Space Accounting

`ubifs_change_lp()` is the central mutation function. It ensures a dirty copy exists through `ubifs_lpt_lookup_dirty()` when needed, updates free/dirty values and flags, adjusts empty/taken-empty/index counters, recomputes total free/dirty/used/dead/dark space under `space_lock`, changes category placement, and adjusts `idx_gc_cnt`. `ubifs_change_one_lp()` and `ubifs_update_one_lp()` are convenience wrappers that take/release lprops locking around a single LEB update.

`ubifs_calc_dark()` estimates unusable "dark" space from a free+dirty byte count. Space smaller than `dark_wm` is treated as dark, while larger regions cap at `dark_wm` except for a small interval where `MIN_WRITE_SZ` is assumed recoverable. This feeds budgeting and GC decisions.

`ubifs_get_lp_stats()` snapshots aggregate lprops statistics. `ubifs_read_one_lp()` reads a single LEB's properties without mutating them.

## Fast Find APIs

`ubifs_fast_find_free()` returns the top free heap entry. `ubifs_fast_find_empty()` returns the first empty-list entry. `ubifs_fast_find_freeable()` returns a non-index LEB whose content is all free/dirty. `ubifs_fast_find_frdi_idx()` returns an index LEB with all free/dirty space. All require `lp_mutex` and assert that returned LEBs are not taken and have category-appropriate flags.

## Debug Validation

`dbg_check_cats()` verifies list and heap membership, category-specific invariants, `freeable_cnt`, and `idx_gc_cnt`. `dbg_check_heap()` checks heap pointer consistency, hpos values, duplicate entries, and correspondence with LPT lookup.

`scan_check_cb()` is the heavy validation callback for `dbg_check_lprops()`. It verifies category placement, scans non-empty/non-freeable LEBs with `ubifs_scan()`, classifies data versus index content, asks the TNC whether scanned nodes are live, computes used/free/dirty bytes, tolerates documented unclean-unmount cases, and accumulates independently calculated totals. `dbg_check_lprops()` first syncs all write-buffers, scans the LPT range, compares calculated totals with `c->lst`, validates dead/dark accounting, and then checks categories.

## Invariants and Consumers

This file is central to allocation and GC. Journal reservation uses free-space categories, GC uses dirty/freeable categories, commit uses category replacement and index-GC counts, and budgeting consumes global totals. Correct locking matters: category mutations require `lp_mutex`, aggregate counters use `space_lock`, and debug full scans avoid taking the LPT mutex because they run during commit-start style locked contexts.
