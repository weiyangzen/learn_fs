# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/alloc_repair.c

## Purpose
Repairs the AG free-space btrees, rebuilding both bnobt and cntbt from reverse-map information. The core model is: free space equals gaps in rmap coverage plus old `OWN_AG` allocation-btree blocks, minus rmapbt and AGFL blocks.

## Main Entry Points
- `xrep_setup_ag_allocbt`: flushes busy extents before scrub/repair.
- `xrep_allocbt`: full bnobt/cntbt rebuild for an AG.
- `xrep_revalidate_allocbt`: re-scrubs both btrees after rebuild by temporarily switching scrub type.

## Key Behavior
`xrep_abt_find_freespace` walks the rmapbt, records gaps as free extents, records `OWN_AG` blocks as possible old allocation btree blocks, records rmapbt path blocks, reads AGFL, and subtracts rmapbt/AGFL blocks from `OWN_AG` to identify old bnobt/cntbt blocks to reap.

Free extents are stored in an `xfarray`, sorted first by length for space reservation and cntbt construction, and later by block number for bnobt construction. `xrep_abt_reserve_space` iteratively reserves free extents for the new btrees until the computed btree geometry converges. Reserved blocks are tracked through `xrep_newbt`.

`xrep_abt_build_new_trees` creates staged bnobt and cntbt cursors, bulk-loads cntbt then bnobt, commits staged roots to the AGF, recalculates AGF counters, reinitializes perag AGF state, disposes unused reservations, rolls the AG transaction, and then `xrep_abt_remove_old_trees` reaps the old btree blocks.

## Dependencies and Interactions
Requires rmapbt. Uses free-space, rmap, ialloc, refcount, newbt, xfile/xfarray, AG block bitmap, and reaping helpers. It relies on AGF being readable enough to access rmapbt and AGFL during reconstruction.

## Failure Handling
Busy extents must be flushed before starting and must remain empty at repair time, otherwise repair returns `-EDEADLOCK`. All reserved newbt state is canceled on failure. Alternate perag btree heights are set during repair to keep write verifiers from rejecting old or new btree blocks while both can be in flight.
