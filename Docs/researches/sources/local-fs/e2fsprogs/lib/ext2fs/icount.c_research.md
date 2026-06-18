# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/icount.c

## Role

Provides an efficient inode reference-count abstraction used by fsck-style passes.

## Main Flow

- Stores count 1 in a bitmap (`single`) and counts greater than one in a sorted list.
- Optional `multiple` bitmap accelerates increment-heavy workloads by tracking list membership.
- Optional `fullmap` stores direct 16-bit counts for increment mode when allocation succeeds.
- Optional TDB backend stores counts externally when `CONFIG_TDB` is enabled.
- Public operations create/free, fetch, increment, decrement, store, validate, and size-query counts.

## Important Details

- Counts are internally 32-bit for list/TDB but public fetches clamp with `icount_16_xlate()` at 65500.
- `get_icount_el()` uses cursor locality plus binary search, with append fast path for sequential loads.
- `insert_icount_el()` resizes based on observed inode density and minimum growth of 100 entries.
- Creation size defaults to estimated directory count plus 2% of total inodes.

## Dependencies

Uses inode bitmaps, `ext2fs_get_num_dirs()`, ext2fs memory helpers, optional TDB, and test filesystem setup under `DEBUG`.

## Risks / Notes

- TDB fetch returns `tdb_error + EXT2_ET_TDB_SUCCESS` even for missing keys while setting count to zero; callers generally ignore the helper’s return in public fetch.
- `fullmap` is indexed by inode number and allocates `num_inodes` entries, while valid inodes include `num_inodes`; this deserves bounds review.
