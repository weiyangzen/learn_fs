# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_leaf.c

## Purpose
Implements XFS leaf-format directory operations and shared leaf-block helpers. It covers v2/v3 leaf header conversion, leaf1/leafn verification, block-to-leaf and node-to-leaf format transitions, leaf-format add/lookup/remove/replace, stale-entry compaction, hash searching, and leaf bestfree table logging.

## Main Entry Points
- `xfs_dir2_leaf_hdr_from_disk()` / `xfs_dir2_leaf_hdr_to_disk()` normalize v2/v3 leaf headers into `xfs_dir3_icleaf_hdr`.
- `xfs_dir3_leaf_read()` and `xfs_dir3_leafn_read()` read leaf1 and leafn blocks with CRC/owner checks.
- `xfs_dir3_leaf_get_buf()` initializes a new leaf block.
- `xfs_dir2_block_to_leaf()` converts a block-format directory into leaf form.
- `xfs_dir2_leaf_addname()`, `xfs_dir2_leaf_lookup()`, `xfs_dir2_leaf_removename()`, and `xfs_dir2_leaf_replace()` implement leaf-format directory mutation.
- `xfs_dir2_leaf_search_hash()` performs binary search over sorted leaf hash entries.
- `xfs_dir2_leaf_trim_data()` removes trailing empty data blocks from leaf-form directories.
- `xfs_dir2_node_to_leaf()` converts a simple node-form directory back to leaf/block form when possible.

## Internal Mechanics
Leaf entries are sorted by hash and can contain stale placeholders with `XFS_DIR2_NULL_DATAPTR`. Insertions either shift entries, reuse the nearest stale entry, compact all but one stale entry, or escalate to node form if the leaf block cannot hold the new entry or bests-table growth. Data-block allocation and dirent creation are delegated to `xfs_dir2_data_*` helpers, while the leaf tail stores per-data-block bestfree values for leaf1 directories.

Lookups binary-search to the first matching hash and then scan equal-hash entries, reading data blocks as needed and preserving case-insensitive matches until an exact match is found. Removal marks a leaf entry stale, frees the data entry, updates the bests table, may shrink empty trailing data blocks, and then attempts conversion back to block form.

## Dependencies
Uses directory data helpers from `xfs_dir2_data.c`, block-format conversion helpers, node-format helpers, DA buffer and bmap operations, transaction logging, buffer ops, tracepoints, and directory health marking.

## Risks and Notes
Leaf format depends on tight free-space accounting between leaf entries, leaf tail bests entries, and data block bestfree headers. Conversion paths assume specific block ordering: block-to-leaf creates the first leaf block at the leaf offset, and node-to-leaf only proceeds when the node root is already a single leafn block and free-space blocks can be removed. `xfs_dir2_leaf_search_hash()` assumes the leaf entry table is non-empty, so callers must maintain that precondition.
