# File Research: sources/os/linux/linux-stable/fs/ubifs/lprops.c

## Role

Maintains UBIFS logical eraseblock properties and their category structures. Lprops track per-LEB free, dirty, index, taken, and category state. Fast category lookups drive journal allocation, garbage collection, and commit cleanup.

## Categories and Heaps

LEBs are categorized into heaps or lists:

- `LPROPS_FREE`: non-index LEBs with free space.
- `LPROPS_DIRTY`: non-index LEBs dirty enough for GC.
- `LPROPS_DIRTY_IDX`: index LEBs with reclaimable free+dirty space.
- `LPROPS_EMPTY`: completely free LEBs.
- `LPROPS_FREEABLE`: non-index LEBs whose free+dirty equals the full LEB.
- `LPROPS_FRDI_IDX`: index LEBs whose free+dirty equals the full LEB.
- `LPROPS_UNCAT`: taken, unsuitable, or heap-overflow fallback entries.

Heap categories are ordered by free space, dirty space, or free+dirty space depending on category. `move_up_lpt_heap()`, `adjust_lpt_heap()`, `add_to_lpt_heap()`, `remove_from_lpt_heap()`, and `lpt_heap_replace()` maintain those structures.

`ubifs_add_to_cat()`, `ubifs_remove_from_cat()`, `ubifs_replace_cat()`, and `ubifs_ensure_cat()` manage membership in heaps/lists.

## Categorization

`ubifs_categorize_lprops()` assigns categories based on:

- `LPROPS_TAKEN`
- full free space
- full free+dirty space
- `LPROPS_INDEX`
- dirty thresholds such as `dead_wm`
- minimum index-node size
- whether dirty exceeds free for data LEB GC usefulness

`change_category()` reclassifies LEBs after updates or adjusts heap position if the category is unchanged.

## Space Accounting

`ubifs_change_lp()` is the only function allowed to mutate lprops. It:

- Ensures a dirty/COW-safe lprops copy exists.
- Updates global free, dirty, used, empty, index, dead, dark, and taken-empty counters.
- Aligns free and dirty values to 8 bytes.
- Handles index flag transitions.
- Recalculates category membership.
- Updates `idx_gc_cnt`.

`ubifs_change_one_lp()` and `ubifs_update_one_lp()` are lookup wrappers for replacing or incrementing LEB properties. `ubifs_read_one_lp()` copies one LEB’s properties out under lprops locking.

`ubifs_calc_dark()` computes unusable “dark” space below or around the dark watermark, supporting conservative free-space budgeting.

## Fast Lookup Helpers

The file provides quick accessors used by journal allocation, GC, and commit:

- `ubifs_fast_find_free()` returns the best heap entry with free space.
- `ubifs_fast_find_empty()` returns an empty-list entry.
- `ubifs_fast_find_freeable()` returns a non-index freeable LEB.
- `ubifs_fast_find_frdi_idx()` returns a freeable dirty index LEB.

These helpers assume `lp_mutex` is held and assert category invariants.

## Debug Validation

`dbg_check_cats()` validates list and heap membership, freeable counts, index-GC count, and taken/index invariants.

`dbg_check_heap()` checks heap positions, duplicate entries, category flags, and LPT lookup consistency.

`scan_check_cb()` and `dbg_check_lprops()` can rescan flash and TNC state to verify lprops accounting. They synchronize all write-buffers before scanning, tolerate some unclean-unmount cases, distinguish index/data LEBs, compute used/free/dirty from live TNC nodes, and compare totals against stored global lprops stats.

## Research Notes

This file is UBIFS’s space-classification substrate. `gc.c` depends on these categories to choose reclaim targets, `journal.c` depends on them to find writable space, and commit/GC index handling depends on the distinction between normal freeable LEBs and delayed index freeable LEBs.
