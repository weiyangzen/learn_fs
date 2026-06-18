# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_leaf.c

## Purpose

`xfs_dir2_leaf.c` implements the single-leaf directory format and the leaf-block half of directory format transitions. Leaf-format directories have one leaf block containing hash/address entries plus a tail `bests` table that records the largest free space in each data block. This file handles:

- v2/v3 leaf header decoding/encoding and verifier operations.
- Creating and reading leaf1/leafn buffers.
- Converting block-format directories to leaf-format.
- Adding, looking up, removing, and replacing entries in leaf-format directories.
- Compacting stale leaf entries and finding insertion positions.
- Trimming trailing empty data blocks.
- Converting node-format directories back to leaf-format when only one leaf remains.

## Header and Buffer Operations

`xfs_dir2_leaf_hdr_from_disk` and `xfs_dir2_leaf_hdr_to_disk` normalize v2/v3 leaf headers into `struct xfs_dir3_icleaf_hdr`. The in-core header carries decoded sibling links, magic, count/stale counts, and a direct pointer to on-disk entries.

Read/write verification flows through:

- `xfs_dir3_leaf_verify`, which first uses `xfs_da3_blkinfo_verify`, then decodes the leaf header and calls `xfs_dir3_leaf_check_int`.
- `xfs_dir3_leaf_check_int`, which checks count bounds, leaf-entry/table overlap for leaf1, optional hash ordering, stale count consistency, and valid bests-table references.
- `xfs_dir3_leaf_header_check`, which validates owner-specific v3 fields after read.
- `xfs_dir3_leaf1_buf_ops` and `xfs_dir3_leafn_buf_ops`, which distinguish leaf1 from leafn buffer types.

## Format Transitions

`xfs_dir2_block_to_leaf` grows the directory into the leaf space, initializes a leaf1 block, copies the block-format leaf entries into it, frees the old leaf/tail region inside the former block directory, changes the data block magic from block to data, and initializes the leaf tail bests table from the data block's largest free entry.

`xfs_dir2_node_to_leaf` is the reverse of `xfs_dir2_leaf_to_node` from `xfs_dir2_node.c`. It only succeeds when the node tree has a single leafn block and the freespace table can fit into leaf1 form. It trims trailing empty freespace blocks, reads the single freespace block, compacts stale leaf entries, changes the leafn block to leaf1, copies free-block `bests` into the leaf tail, removes the freespace block, and finally tries to downgrade further to block format through `xfs_dir2_leaf_to_block`.

## Leaf Entry Management

Insertion is built around two helpers:

- `xfs_dir3_leaf_find_stale` finds nearby stale slots around the insertion index.
- `xfs_dir3_leaf_find_entry` either opens a new slot by memmove or reuses a stale slot, preferring the move with the smaller entry shift.

`xfs_dir3_leaf_compact` removes all stale entries. `xfs_dir3_leaf_compact_x1` removes all but one stale entry so insertion can reuse the remaining stale slot with minimal movement.

`xfs_dir2_leaf_search_hash` performs a binary search by hash and rewinds to the first duplicate hash value, which supports duplicate-hash lookup and insertion.

## Directory Operations

`xfs_dir2_leaf_addname`:

- Reads the leaf block and finds the hash insertion point.
- Prefers a data block already containing the same hash when it has enough space, improving lookup locality for duplicate hashes.
- Searches the leaf tail bests table for a data block with enough free space, or allocates a new data block.
- Converts to node format if the leaf block cannot fit another entry or bests slot.
- Consumes space from the selected data block, writes the new dirent, updates `bestsp`, inserts the leaf entry, logs modified ranges, and rechecks leaf/data consistency.

`xfs_dir2_leaf_lookup` delegates to `xfs_dir2_leaf_lookup_int`, which scans all duplicate-hash entries, reads data blocks lazily as the referenced db changes, supports case-insensitive matches, and returns the matching data buffer and leaf index.

`xfs_dir2_leaf_removename` marks the leaf entry stale, frees the data entry, updates the data block and leaf `bests` value, tries to remove empty data blocks, compacts trailing `bests` entries, then calls `xfs_dir2_leaf_to_block` to see if the directory can downgrade to block format.

`xfs_dir2_leaf_replace` updates only the inode number and file type of the matched data entry, then logs the dirent.

## Dependencies and Interactions

This file depends heavily on `xfs_dir2_data.c` for data-block allocation/freeing and on `xfs_dir2_node.c` for leaf-to-node conversion and free-block reads. It also uses generic directory/attribute btree helpers (`xfs_da_*`) for block allocation and shrinking.

## Implementation Notes

Stale leaf entries are intentionally retained during remove to avoid immediate large memmoves, then compacted opportunistically when insertion, conversion, or coalescing makes it worthwhile. The bests table moves backward from the end of the leaf block, so extending it requires decrementing `bestsp` and moving existing entries.
