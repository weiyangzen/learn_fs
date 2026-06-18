# File Research: sources/local-fs/xfsprogs/repair/incore_ext.c

## Role

`incore_ext.c` implements AVL/btree-backed extent tracking for duplicate extents and rebuilt free-space trees.

## Extent Structure

The file manages four structures:

- Per-AG duplicate extent btrees.
- Per-AG free extent bno AVL trees.
- Per-AG free extent bcnt AVL trees.
- A realtime duplicate extent AVL64 tree.

## Duplicate Extents

`add_dup_extent` inserts a per-AG duplicate block range into a btree keyed by start block, storing end block as value.

`search_dup_extent` tests whether a requested AG block range overlaps any duplicate extent. It checks the found range and previous range.

`release_dup_extent_tree` clears a per-AG duplicate tree after phase 4 has processed that AG.

## Free Extent Trees

`add_bno_extent`, `findfirst_bno_extent`, `find_bno_extent`, and `get_bno_extent` manage free extents sorted by starting block.

`add_bcnt_extent`, `findfirst_bcnt_extent`, `findbiggest_bcnt_extent`, `findnext_bcnt_extent`, and `get_bcnt_extent` manage free extents sorted by block count. Equal-sized extents are stored in an ordered linked list anchored by the AVL node.

The bcnt code swaps node contents in a few cases to preserve AVL anchor identity while inserting/removing entries from equal-size lists.

## Realtime Duplicate Extents

Realtime duplicate extents use 64-bit AVL keys because realtime extent numbers can exceed AG block widths.

`add_rt_dup_extent` merges overlapping or adjacent realtime duplicate ranges before insertion.

`search_rt_dup_extent` tests whether a realtime extent is in the duplicate tree.

`free_rt_dup_extent_tree` releases the realtime duplicate tree descriptor.

## Initialization and Teardown

`incore_ext_init` allocates all per-AG descriptor tables, initializes btrees and AVL trees, initializes locks, and initializes the realtime duplicate tree.

`incore_ext_teardown` destroys per-AG duplicate trees and frees bno/bcnt descriptor arrays. Realtime duplicate teardown is separate.

## Count Helpers

- `count_bno_extents_blocks`: counts bno extents and total blocks in an AG.
- `count_bno_extents`: counts bno extents.
- `count_bcnt_extents`: counts bcnt extents.

## Interactions

Phase 4 builds duplicate extent lists from the global block map, then inode scans query those lists to decide which inodes must be cleared. Phase 5 uses bno/bcnt free extent trees to rebuild allocation btrees.
