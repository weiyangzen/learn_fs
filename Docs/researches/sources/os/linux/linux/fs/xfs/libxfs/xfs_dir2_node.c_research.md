# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_node.c

## Purpose

Implements XFS node-format directories: freespace block verification and management, leaf-to-node conversion, leafn add/lookup/split/rebalance/join helpers, data-entry add/remove for node directories, top-level node add/lookup/remove/replace operations, and cleanup of empty freespace blocks.

## Main Interfaces

- Free block mapping and verification: internal `xfs_dir2_db_to_fdb()`, `xfs_dir2_db_to_fdindex()`, `xfs_dir3_free_buf_ops`, `xfs_dir2_free_read()`.
- Free header conversion/allocation: `xfs_dir2_free_hdr_from_disk()`, internal `xfs_dir2_free_hdr_to_disk()`, `xfs_dir3_free_get_buf()`.
- Format conversion: `xfs_dir2_leaf_to_node()`, `xfs_dir2_node_trim_free()`.
- Leafn helpers: `xfs_dir2_leaf_lasthash()`, `xfs_dir2_leafn_lookup_int()`, `xfs_dir2_leafn_order()`, `xfs_dir2_leafn_split()`, `xfs_dir2_leafn_toosmall()`, `xfs_dir2_leafn_unbalance()`.
- Node-format operations: `xfs_dir2_node_addname()`, `xfs_dir2_node_lookup()`, `xfs_dir2_node_removename()`, `xfs_dir2_node_replace()`.

## Control Flow And Behavior

Freespace blocks cover arrays of data-block bestfree values. Header checks verify the free block's expected first data-block index, `nvalid <= free_max_bests`, `nused <= nvalid`, and v5 owner metadata. Free block allocation initializes an empty v2/v3 header and sets buffer type/ops.

Leaf-to-node conversion allocates the first free-space block, copies the leaf1 bests table into it, initializes `nvalid` and `nused`, and changes the single leaf block from leaf1 magic to leafn magic. This separates data-block free-space accounting from the leaf block so the directory can grow a DA btree.

For add lookup, `xfs_dir2_leafn_lookup_for_addname()` searches matching-hash leaf entries for a data block with enough free space, returning the corresponding free block as `state->extrablk` when useful. For normal lookup/removal/replace, `xfs_dir2_leafn_lookup_for_entry()` scans equal hashes, reads data blocks, supports CI matches, and returns the found data block in the DA state.

`xfs_dir2_node_addname()` builds a DA state cursor, uses node lookup to find the insertion point, adds the data entry first via `xfs_dir2_node_addname_int()`, then inserts the leafn entry. If the target leafn is full, it splits and rebalances leaf entries through the generic DA split path. Data-entry addition scans existing free blocks from high to low for space, allocates a new data block and maybe a new free block if needed, carves space with data helpers, writes the dirent, updates the free block bests entry, and returns the new data block/offset for the leaf entry.

Removal uses the DA state to find the leaf and data entry, marks the leaf entry stale, frees the data entry, updates data bestfree, updates or removes the corresponding free-block entry, can punch empty data blocks, fixes btree hash values, joins underfull leaf blocks, and finally tries to convert the node directory back to leaf form. Replacement preserves the new inode/filetype across lookup, then updates the matched data entry and logs it.

Leaf split/rebalance code moves sorted entries between sibling leafn blocks, preserving stale counts and choosing the insertion side. Join checks consider empty blocks, 50% fullness, sibling fit with 25% spare, and prefer retaining the lower-numbered block for gradual directory shrinkage.

## State And Data Structures

Node directories use DA btree paths (`xfs_da_state`) over leafn blocks. Separate free blocks begin at `XFS_DIR2_FREE_OFFSET`; each entry maps to one data block and stores that block's largest free region or `NULLDATAOFF` for a missing/unused data block. The DA state's `extrablk` alternates between free blocks for add operations and data blocks for lookup/remove/replace operations.

## Dependencies

Depends on DA btree lookup/split/join/path-shift/hash-fix code, leaf helpers from `xfs_dir2_leaf.c`, data block helpers from `xfs_dir2_data.c`, directory block grow/shrink helpers, transaction logging, bmap last-offset queries, and corruption/health marking.

## Risks And Invariants

- Free block `firstdb`, `nvalid`, `nused`, and bests entries must match the data block range implied by the free block number.
- Add operations intentionally create the data entry before the leaf entry; error handling must keep transaction state coherent.
- Empty data and free blocks can fail to shrink without reservation; callers intentionally tolerate some `-ENOSPC` cleanup failures.
- Leafn stale entry accounting affects split/join decisions and later format collapse.
- `state->extrablk` meaning depends on operation type and must be set with correct buffer ops/type.
