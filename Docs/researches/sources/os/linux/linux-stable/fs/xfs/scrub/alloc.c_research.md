# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/alloc.c

## Purpose
Scrubs XFS free-space allocation btrees: bnobt and cntbt. It validates individual free-space records, detects mergeable adjacent records, and cross-references each record against the companion allocation btree and other AG metadata.

## Main Entry Points
- `xchk_setup_ag_allocbt`: prepares AG btree scrub and, if repair is possible, runs allocation btree repair setup.
- `xchk_allocbt`: selects bnobt or cntbt according to `sm_type` and invokes generic btree scrub.
- `xchk_xref_is_used_space`: shared xref helper that verifies a range is not present in free-space btrees.

## Key Behavior
Each allocation record is converted to incore format and checked with `xfs_alloc_check_irec`. `xchk_allocbt_mergeable` flags adjacent free-space records that should have been merged. `xchk_allocbt_xref_other` verifies a matching record exists in the other free-space btree. Additional xrefs ensure the free extent is not an inode chunk, has no owner in rmap, is not shared, and is not CoW staging.

## Dependencies and Interactions
Works with generic scrub btree traversal, allocation btree cursors stored in `sc->sa`, rmap/refcount xref helpers, and `alloc_repair.c` setup when repair is enabled.

## Failure Handling
Cross-reference checks are skipped after corruption is already detected or when the target cursor is unavailable. Btree cursor errors are processed through scrub xref helpers so a broken xref tree can be isolated from the tree under examination.
