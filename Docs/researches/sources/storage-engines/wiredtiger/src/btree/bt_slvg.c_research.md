# sources/storage-engines/wiredtiger/src/btree/bt_slvg.c

## Purpose

`bt_slvg.c` implements btree salvage: scanning a damaged WiredTiger file for usable leaf and overflow pages, resolving overlapping ranges by write generation, rebuilding a root, writing merged leaves when needed, freeing discarded blocks, and installing a new checkpoint. The complete 2431-line source was read.

## Important APIs, Types, and Functions

The exported functions are `__wt_salvage` and `__wt_slvg_reconcile_free`. Temporary state is organized into `WT_STUFF` for the salvage run, `WT_TRACK_SHARED` for physical page metadata shared by split chunks, and `WT_TRACK` for logical row/column ranges. Major helpers cover scanning (`__slvg_read`, `__slvg_trk_leaf`, `__slvg_trk_ovfl`), overflow reconciliation (`__slvg_ovfl_reconcile`, `__slvg_ovfl_discard`), range resolution (`__slvg_row_range`, `__slvg_col_range` and overlap helpers), tree rebuild (`__slvg_row_build_internal`, `__slvg_col_build_internal`, merge-leaf builders), checkpointing, and cleanup.

## Control Flow

`__wt_salvage` starts block-manager salvage mode, quietly scans all salvage candidate blocks, verifies pages, tracks row/VLCS leaves and overflow pages, reconciles overflow ownership before key-range selection, discards unused overflow pages, sorts leaf ranges by key and generation, resolves overlaps, detects missing VLCS ranges, builds a replacement internal root, writes merged leaves when ranges were truncated or split, delays freeing original merge blocks until the new tree is built, writes a fresh checkpoint, ends block-manager salvage mode, and frees temporary memory.

Range overlap handling is parallel for row and column pages. Newer generations win; older ranges may be deleted, truncated, or split into multiple `WT_TRACK` chunks. Row-store adjusted starts may require rereading a page to find the first key after a boundary.

## State and Persistence Behavior

Salvage is persistent: it frees ignored/corrupt/discarded blocks, writes replacement merged leaf pages and an internal root, and replaces metadata checkpoints with the salvage result. `WT_TRACK_SHARED` reference counts protect physical pages that have been split into logical chunks. `session->salvage_track` lets reconciliation report overflow frees to salvage tracking instead of freeing blocks immediately.

## Dependencies and Integration Points

The file integrates with block-manager salvage APIs, block-cache reads, disk verification, page instantiation, row/column page formats, reconciliation, eviction, overflow block management, collators, time aggregates, metadata checkpoint APIs, verbose/progress reporting, and scratch allocation.

## Risks and Edge Cases

Salvage may resurrect deleted data because old leaf images can survive page deletion. It discards whole leaves that reference missing or already-claimed overflow pages, favoring coherence over per-key recovery. Delayed block freeing is critical: freeing original pages before the salvage checkpoint succeeds could overwrite data needed by a later salvage attempt. VLCS RLE splits and overflow reuse can force row deletion in merged pages. Row qsort comparison cannot propagate collator errors cleanly.

## Test Signals

Cover valid and corrupt blocks, ignored internal pages, mixed row/column formats, missing and duplicate overflow pages, overlapping ranges with older/newer generations, prefix/middle/suffix range splits, VLCS missing ranges and RLE splits, merged pages with overflow values, no-leaf salvage, checkpoint replacement, and fault injection during read, merge reconciliation, root eviction, and metadata updates.
