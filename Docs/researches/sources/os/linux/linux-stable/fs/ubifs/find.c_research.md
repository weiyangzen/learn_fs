# File Research: sources/os/linux/linux-stable/fs/ubifs/find.c

UBIFS logical eraseblock selection logic for data allocation, garbage collection, index allocation, and in-the-gaps index commit.

Key responsibilities:
- Finds dirty LEBs for garbage collection.
- Finds free data LEBs for writing.
- Finds free/empty LEBs for index commit.
- Saves and later consumes dirty index LEB candidates.
- Falls back from in-memory lprops heaps/lists to LPT scans when needed.

Important routines:
- `valuable()` decides whether scanned lprops should be brought into memory based on category and usefulness.
- `ubifs_find_dirty_leb()` selects a dirty LEB for GC, with special `pick_free` modes and index-reservation protection.
- `ubifs_find_free_space()` finds a data LEB with enough free space, optionally preferring non-empty “squeezed” space, marks it taken, returns the free offset, and unmaps empty/freeable LEBs before use.
- `ubifs_find_free_leb_for_idx()` allocates only empty/freeable LEBs for index use, marks them `LPROPS_TAKEN | LPROPS_INDEX`, and unmaps them.
- `ubifs_save_dirty_idx_lnums()` snapshots dirty index LEBs at commit time, sorts them by dirty+free space, and stores LEB numbers for later in-the-gaps allocation.
- `ubifs_find_dirty_idx_leb()` tries saved dirty-index candidates, then scans all lprops, then falls back to trivial index GC LEBs.

Selection policy:
- In-memory fast paths use lprops category heaps and lists: dirty, dirty index, free, empty, freeable, freeable index, and uncategorized.
- Scans exclude `LPROPS_TAKEN` and usually exclude index LEBs unless specifically searching for index LEBs.
- Empty LEB allocation is constrained by index reservation accounting through `min_idx_lebs`, `idx_lebs`, `idx_gc_cnt`, and `taken_empty_lebs`.
- Data allocation avoids LEBs containing only free+dirty space when dirty data may still be referenced by write buffers.

Cross-file links:
- Depends on lprops/LPT APIs such as `ubifs_lpt_scan_nolock()`, `ubifs_change_lp()`, `ubifs_fast_find_empty()`, and `ubifs_lpt_lookup_dirty()`.
- Used by journal, GC, budgeting, and commit code to reserve physical flash space.
- Debug messages use `dbg_find()` from `debug.h`.

Invariants and risks:
- Returned LEBs are marked `LPROPS_TAKEN` before release to prevent concurrent reuse.
- Empty/freeable LEBs are explicitly unmapped before writing to protect against stale contents after unclean unmount.
- `taken_empty_lebs` is temporarily adjusted while dropping `space_lock`; comments document this as a deliberate pessimistic budgeting tradeoff.
