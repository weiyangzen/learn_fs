# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_node.c

## Purpose

`xfs_dir2_node.c` implements node-format directory support. Node-format directories have btree-managed leafn blocks plus separate freespace blocks that track the largest free area in groups of data blocks. This file handles:

- Free-block verification, read, initialization, logging, and header conversion.
- Leaf1-to-leafn conversion and leafn add/lookup/remove/split/rebalance/coalesce mechanics.
- Node-format add, lookup, remove, and replace operations.
- Data-block allocation and freespace-block accounting for large directories.
- Trimming empty trailing freespace blocks and assisting downgrade from node to leaf.

## Free Block Model

Data block number to free block mapping is:

- `xfs_dir2_db_to_fdb`: maps a data block to the freespace block that contains its bestfree record.
- `xfs_dir2_db_to_fdindex`: maps a data block to its index within that freespace block.

Free block headers are normalized via `xfs_dir2_free_hdr_from_disk` and `xfs_dir2_free_hdr_to_disk`. `xfs_dir3_free_header_check` verifies that `firstdb` matches the expected directory block number range, `nvalid <= free_max_bests`, `nused <= nvalid`, and the v3 owner matches. `xfs_dir2_free_read` requires a block; `xfs_dir2_free_try_read` allows holes for sparse freespace block ranges.

`xfs_dir3_free_get_buf` creates a new free block, initializes the v2/v3 header and owner/uuid fields, and assigns `xfs_dir3_free_buf_ops`.

## Leafn Operations

`xfs_dir2_leaf_to_node` converts a leaf-format directory to node format by allocating the first freespace block, copying the leaf tail bests table into it, setting `nvalid` and `nused`, and changing the leaf1 magic to leafn.

`xfs_dir2_leafn_add` inserts a leaf entry into a leafn block. It compacts stale entries only when needed, rejects negative indexes as corruption, and returns `-ENOSPC` when a full leaf without stale entries must be split.

`xfs_dir2_leafn_lookup_int` dispatches between addname lookup and normal entry lookup:

- `xfs_dir2_leafn_lookup_for_addname` searches duplicate-hash entries for a data block with enough space and returns a freespace block in `state->extrablk` if useful.
- `xfs_dir2_leafn_lookup_for_entry` scans duplicate-hash entries, reads referenced data blocks, supports case-insensitive matches, and returns a data block in `state->extrablk`.

`xfs_dir3_leafn_moveents`, `xfs_dir2_leafn_order`, and `xfs_dir2_leafn_rebalance` move sorted leaf entries between sibling leaves during split/rebalance while preserving stale counts and updating insertion location state.

`xfs_dir2_leafn_split` allocates a new leafn block, rebalances entries, links the new block into the DA btree sibling chain, inserts the pending leaf entry, and updates last-hash values.

`xfs_dir2_leafn_toosmall` and `xfs_dir2_leafn_unbalance` implement post-remove coalescing decisions. Empty leaves can be deleted directly; underfilled leaves can be merged with a sibling if combined live entries leave enough free space.

## Node Directory Operations

`xfs_dir2_node_addname` allocates a DA state cursor, runs btree lookup to find insertion position, calls `xfs_dir2_node_addname_int` to create the data entry, then calls `xfs_dir2_leafn_add`. If the target leaf is full, it uses `xfs_da3_split`. The ordering is important: the data entry is installed before the leaf entry or split, relying on reservations and later leaf insertion to complete namespace visibility.

`xfs_dir2_node_addname_int` first calls `xfs_dir2_node_find_freeblk`, which either uses the lookup-provided freespace block or scans freespace blocks backward for an entry large enough. If no data block has room, `xfs_dir2_node_add_datablk` allocates a data block and creates/extends the corresponding free block. The function then consumes data free space, writes the dirent, updates/logs the free-block `bests` entry, and records the data block and offset in `args` for leaf insertion.

`xfs_dir2_node_lookup` is mostly a wrapper around `xfs_da3_node_lookup_int`; it handles case-insensitive lookup result finalization and releases cursor/data buffers.

`xfs_dir2_node_removename` looks up the entry, calls `xfs_dir2_leafn_remove` to mark the leaf stale and free the data dirent, fixes btree hash values, joins underfull leaves if needed, and attempts node-to-leaf downgrade.

`xfs_dir2_node_replace` looks up the entry, restores the caller's replacement inode/filetype after lookup overwrites args, updates the data dirent, and releases buffers.

`xfs_dir2_node_trim_free` removes a trailing freespace block if it has no used entries.

## Consistency and Corruption Handling

The file marks buffers corrupt and calls `xfs_da_mark_sick` on impossible indexes, missing freespace entries, or mismatched free-block allocation results. Free block verifier limitations are acknowledged with a comment that bounds checking for `xfs_dir3_icfree_hdr` could be stronger.

## Dependencies and Interactions

This file is the node-format partner to `xfs_dir2_leaf.c`; it exposes `xfs_dir2_leaf_to_node`, leafn helpers, node operations, free-block reads, and trimming helpers through `xfs_dir2_priv.h`. It relies on `xfs_dir2_data.c` for data block manipulation and on DA btree helpers for path lookup, split, join, hash fixes, and block allocation.
