# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_leaf.c

## Purpose

Implements XFS leaf-format directory blocks and shared leaf helpers used by leaf and node directories: v2/v3 leaf header conversion, leaf verification, buffer operations, leaf block initialization, block-to-leaf conversion, add/lookup/remove/replace for single-leaf directories, stale-entry compaction, bests-table logging, data-block trimming, and node-to-leaf collapse.

## Main Interfaces

- Header conversion and verification: `xfs_dir2_leaf_hdr_from_disk()`, `xfs_dir2_leaf_hdr_to_disk()`, `xfs_dir3_leaf_check_int()`, `xfs_dir3_leaf_header_check()`.
- Buffer reads and allocation: `xfs_dir3_leaf_read()`, `xfs_dir3_leafn_read()`, `xfs_dir3_leaf_get_buf()`, `xfs_dir3_leaf1_buf_ops`, `xfs_dir3_leafn_buf_ops`.
- Format conversion: `xfs_dir2_block_to_leaf()`, `xfs_dir2_node_to_leaf()`.
- Leaf-format operations: `xfs_dir2_leaf_addname()`, `xfs_dir2_leaf_lookup()`, `xfs_dir2_leaf_removename()`, `xfs_dir2_leaf_replace()`.
- Shared leaf helpers: `xfs_dir3_leaf_find_entry()`, `xfs_dir3_leaf_compact()`, `xfs_dir3_leaf_compact_x1()`, `xfs_dir3_leaf_log_ents()`, `xfs_dir3_leaf_log_header()`, `xfs_dir2_leaf_search_hash()`, `xfs_dir2_leaf_trim_data()`.

## Control Flow And Behavior

Leaf verification decodes v2/v3 headers into an in-core header, validates DA block info, bounds the entry count, checks that leaf entries do not overlap a leaf1 bests table, and optionally checks hash ordering, stale count, and leaf1 bests-table address coverage. Reads also validate v5 owners after generic verification.

Block-to-leaf conversion allocates the first leaf-space block, initializes it as a leaf1 block, copies embedded block leaf entries into the new leaf, marks the old embedded leaf/tail area in the data block free, changes the old block directory to a data block, and seeds the leaf1 bests table from the data block bestfree value.

`xfs_dir2_leaf_addname()` reads the leaf1 block, finds the hash insertion point, prefers a data block already containing the same hash if it has room, otherwise scans the leaf bests table or allocates a new data block. It ensures leaf space exists for a new entry or bests entry, compacts stale entries if useful, converts to node form when the leaf no longer fits, writes the new data entry, updates data bestfree and leaf bests, inserts the sorted leaf record, and logs all changed ranges.

Lookup binary-searches to the first matching hash, scans equal-hash entries, reads data blocks as needed, supports exact and case-insensitive matches, and returns inode/filetype plus actual case-preserved name when needed. Removal marks the data entry free, marks the leaf entry stale, updates the leaf1 bests table, drops empty data blocks when possible, and then tries to convert the directory to block form. Replacement updates only the target data entry inode number and filetype.

Node-to-leaf conversion is attempted when a node directory has only one leafn block and one freespace block. It trims trailing empty freespace blocks, verifies the leafn plus freespace data fits in one leaf1 block, compacts stale leaf entries, changes the leafn to leaf1, copies the free block bests table into the leaf tail area, frees the separate free block, and then tries leaf-to-block conversion.

## State And Data Structures

Leaf1 directories have a sorted leaf-entry array plus a tail and bests table recording the largest free space in each data block. Leafn blocks are similar leaf arrays without the bests tail and are used below DA btree nodes. `xfs_dir3_icleaf_hdr` abstracts v2/v3 on-disk header differences and points to the on-disk leaf entries.

## Dependencies

Depends on directory data-block helpers, block-format conversion, node-format conversion, DA allocation and btree helpers, transaction logging, bmap last-offset queries, data/free block shrink helpers, and directory health marking through lower-level read functions.

## Risks And Invariants

- Leaf entries must stay sorted by hash, with duplicate hashes preserving scan semantics.
- Leaf stale counts must match entries whose address is `XFS_DIR2_NULL_DATAPTR`.
- Leaf1 bests entries must stay synchronized with data-block bestfree values and data block lifetime.
- Format conversions must not lose free-space records or leave buffers with the wrong verifier/type.
- Case-insensitive lookup must retain the first CI match while still preferring an exact match.
