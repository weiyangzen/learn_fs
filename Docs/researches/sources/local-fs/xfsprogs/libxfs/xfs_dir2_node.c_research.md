# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_node.c

## Purpose
Implements XFS node-format directory support: free-space block verification/management, leaf1-to-leafn conversion, leafn lookup/add/remove/split/rebalance/join helpers, node-format add/lookup/remove/replace, and trimming empty free-space blocks.

## Main Entry Points
- `xfs_dir2_free_hdr_from_disk()` and the internal `xfs_dir2_free_hdr_to_disk()` abstract v2/v3 free-block headers.
- `xfs_dir2_free_read()` reads free-space blocks; `xfs_dir2_free_try_read()` tolerates holes.
- `xfs_dir2_leaf_to_node()` converts a leaf-format directory into node form by moving the leaf bests table to a free block.
- `xfs_dir2_leafn_lookup_int()` dispatches lookup behavior for addname vs entry lookup.
- `xfs_dir2_leafn_split()`, `xfs_dir2_leafn_toosmall()`, and `xfs_dir2_leafn_unbalance()` support DA btree split/join mechanics.
- `xfs_dir2_node_addname()`, `xfs_dir2_node_lookup()`, `xfs_dir2_node_removename()`, and `xfs_dir2_node_replace()` are top-level node-format operations.
- `xfs_dir2_node_trim_free()` removes trailing unused free-space blocks.

## Internal Mechanics
Node directories store hash-indexed leafn blocks separately from data blocks and maintain free-space summaries in blocks starting at `XFS_DIR2_FREE_OFFSET`. `xfs_dir2_db_to_fdb()` and `xfs_dir2_db_to_fdindex()` map data-block numbers to their free-space block and index. Addname first uses the DA btree lookup path to find the leaf insertion point and possibly a preferred free block, then finds or allocates a data block, creates the data entry, updates the free-space summary, and inserts a leafn entry. If the leaf is full, DA split calls `xfs_dir2_leafn_split()`.

Removal marks the leaf entry stale, frees the dirent in its data block, updates or removes the free-space entry, can shrink empty data/free blocks, fixes btree hashes, may join underfull leaf blocks, and finally tries node-to-leaf conversion.

## Dependencies
Depends on DA btree state/path operations, leaf helpers from `xfs_dir2_leaf.c`, data helpers from `xfs_dir2_data.c`, inode grow/shrink and bmap helpers, transaction logging, buffer verification, tracepoints, and XFS health marking.

## Risks and Notes
The free-space verifier has an explicit `XXX` noting that `xfs_dir3_free_verify()` should bounds-check the decoded in-core free header. Node add/remove has delicate ownership of `state->extrablk` buffers because that slot alternates between free blocks and data blocks depending on the operation. Error paths around no-space-reservation operations intentionally leave some empty blocks for later cleanup; callers must tolerate holes and stale summaries.
