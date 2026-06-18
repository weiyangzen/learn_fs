# File Research: sources/os/linux/linux/fs/ubifs/find.c

Read completely: 963 lines.

This file implements UBIFS logical eraseblock selection for data allocation, garbage collection, and index allocation/GC. It searches lprops heaps/lists first and scans the LPT only when in-memory categories do not contain a suitable LEB.

Main entry points: `ubifs_find_dirty_leb`, `ubifs_find_free_space`, `ubifs_find_free_leb_for_idx`, `ubifs_save_dirty_idx_lnums`, and `ubifs_find_dirty_idx_leb`.

Key behavior:
- `valuable` decides whether lprops discovered during an LPT scan should be cached in memory based on category, heap capacity, and useful free+dirty space.
- dirty-LEB selection prefers dirty or dirty-index heaps, can pick empty/freeable LEBs when requested, avoids index-reserved LEBs when necessary, and marks the result `LPROPS_TAKEN`.
- free-space selection balances empty LEB preservation for index/commit needs with allocation of non-index LEBs that have enough free space; offset zero results are unmapped before use.
- index allocation only uses empty/freeable LEBs, marks them `LPROPS_TAKEN | LPROPS_INDEX`, and unmaps before returning.
- dirty index selection uses a commit-time sorted dirty-index array first, then full LPT scan, then trivial-GC candidates.

Important interactions: tightly coupled to lprops categories/heaps, LPT scanning, budgeting state (`min_idx_lebs`, `idx_lebs`, `taken_empty_lebs`), journal/GC allocation, and commit-time in-the-gaps index writing.

Reliability notes: the file carefully avoids selecting `LPROPS_TAKEN` LEBs, index LEBs for data when reserved index space is tight, and free+dirty data LEBs whose obsolete content may still depend on write-buffer state. Short-lived adjustments to `taken_empty_lebs` make budgeting pessimistic while the lprops update completes.
