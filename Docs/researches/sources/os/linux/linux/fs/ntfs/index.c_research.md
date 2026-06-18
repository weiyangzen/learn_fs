# File Research: sources/os/linux/linux/fs/ntfs/index.c

## Purpose
Implements the generic NTFS index B+tree engine used by directories and NTFS metadata indexes, including lookup, traversal, insertion, block splitting, bitmap management, deletion, and dirty writeback of index blocks.

## Key Elements
`ntfs_index_context` instances are allocated by `ntfs_index_ctx_get()` and hold the current root/block entry, attribute context, index allocation inode, parent VCN stack, parent positions, block geometry, and dirty state. `ntfs_index_lookup()` locates keys by reading resident `$INDEX_ROOT`, validating collation rules, descending into `$INDEX_ALLOCATION` blocks via child VCNs, and returning either a found entry or the insertion position for `-ENOENT`.

The file contains low-level index entry helpers for first/next/previous/last entry lookup, deletion, insertion, VCN pointer access, duplication with or without child VCN, and entry counting. Validation routines check index entry key/data bounds and index block magic, VCN, allocation size, entry offset, and index length.

Mutation support manages `$BITMAP` for index blocks (`ntfs_ibm_add()`, set/clear/get-free), creates `$INDEX_ALLOCATION` when a small resident root becomes large, moves root entries into a new index block (`ntfs_ir_reparent()`), expands or truncates resident roots, splits full blocks around a median, propagates medians upward, and retries when splits change the tree shape. `ntfs_index_add_filename()` wraps FILE_NAME attributes into directory index entries.

Deletion handles simple root/block removal, internal-node removal by replacing with successor entries, leaf block deletion, bitmap clearing, parent reparenting, and root collapse back to a leaf when the tree shrinks. Traversal helpers `ntfs_index_walk_down()`, private walk-up logic, and `ntfs_index_next()` provide in-order iteration for directory reads.

## Dependencies And Integration
Depends on NTFS collation, attribute-list, MFT, attribute I/O, and inode helpers. Directory code uses it for lookup/iteration and directory entry add/remove; inode sync uses it to update FILE_NAME entries in parent indexes.

## Behavior/Risks
The implementation assumes index blocks fit in `PAGE_SIZE` because inode setup rejects larger block sizes. Dirty index blocks are written with MST fixups through `ntfs_inode_attr_pwrite()`; synchronous write mode frees the in-memory block after success. Parent stack depth is capped by `MAX_PARENT_VCN` and returns `-EOPNOTSUPP` for overly deep trees.
