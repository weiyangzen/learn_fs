# File Research: sources/os/linux/linux/fs/xfs/scrub/btree.c

## Role
Implements the generic XFS scrub btree walker for ondisk and inode-rooted btrees. It validates structural consistency while walking every node and leaf, delegates per-record semantic checks to a caller-supplied callback, and records scrub outcomes through `xfs_scrub_metadata.sm_flags`.

## Main Interfaces
- `xchk_btree_process_error` and `xchk_btree_xref_process_error`: normalize btree operation errors into scrub corruption or xref-failure flags where appropriate.
- `xchk_btree_set_corrupt`, `xchk_btree_xref_set_corrupt`, `xchk_btree_set_preen`: mark btree block findings and emit inode-fork or AG btree tracepoints depending on cursor type.
- `xchk_btree`: top-level nonrecursive btree traversal.

## Important Internal Flow
- Allocates `struct xchk_btree` sized by cursor height; rejects absurd heights if the context would exceed one page.
- Initializes a root pointer from the cursor, validates it with `__xfs_btree_check_ptr`, and loads the root through `xfs_btree_lookup_get_block`.
- Walks the tree depth-first by manipulating `cur->bc_levels[level].ptr`.
- At leaf level, `xchk_btree_rec` enforces record ordering and parent low/high key containment before invoking the caller's record scrub callback.
- At node levels, `xchk_btree_key` enforces key ordering and parent containment before descending through child pointers.
- Stops early on operational errors, termination requests, or a detected primary corruption flag.

## Validation Coverage
- Pointer validity through `__xfs_btree_check_ptr`.
- Btree block verifier through `__xfs_btree_check_block` plus `xchk_buffer_recheck`.
- Minimum-record constraints, with a compatibility exception for historical data-fork bmbt roots that were unnecessarily spilled when attr forks were added.
- Sibling pointer consistency by duplicating the cursor and comparing adjacent parent-level pointers.
- Parent key consistency for ordinary and overlapping-key btrees.
- Owner consistency against bnobt/rmapbt, with deferred owner checks for bno/rmap self-scrubs to avoid disturbing the active cursor.

## Dependencies
Uses core btree cursor operations from `xfs_btree`, scrub common helpers from `scrub/common.h`, owner info from `xfs_owner_info`, AG context setup through `xchk_ag_init_existing`, and xref helpers such as `xchk_xref_is_used_space` and `xchk_xref_is_only_owned_by`.

## Invariants and Edge Cases
- Inode-rooted btrees have no external pointer to their root, so the synthetic root pointer is accepted.
- Null siblings must correspond to no adjacent parent entry; non-null siblings must match adjacent parent pointers.
- Root blocks may have fewer records than `minrecs`; non-root underfull blocks are corrupt except for the inode-root spill exception.
- If self-xref discovers that the cursor for the btree being scanned is no longer available, `bs->cur` is cleared to shut down further owner checks safely.
