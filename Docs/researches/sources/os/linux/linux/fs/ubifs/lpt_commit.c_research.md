# File Research: sources/os/linux/linux/fs/ubifs/lpt_commit.c

## Role

Implements commit-time LPT handling: selecting dirty LPT cnodes, laying them out, writing them, maintaining LPT-area lprops, performing trivial and regular LPT garbage collection, freeing obsolete COW nodes, and validating/dumping LPT state for debugging.

## Key APIs

- `ubifs_lpt_start_commit()`
- `ubifs_lpt_end_commit()`
- `ubifs_lpt_post_commit()`
- `ubifs_lpt_free()`
- Debug entries: `dbg_check_ltab()`, `dbg_chk_lpt_free_spc()`, `dbg_chk_lpt_sz()`, `ubifs_dump_lpt_lebs()`

## Important Behavior

Commit starts by checking LPT consistency, optionally running LPT GC if free space is low, doing trivial GC marking, populating lsave for big LPT, building a circular list of dirty cnodes, laying out new node locations, and calculating the LPT hash into the master node.

`get_cnodes_to_commit()` walks the dirty in-memory LPT tree and freezes dirty cnodes by setting `COW_CNODE`. Later modifications in `lpt.c` copy these cnodes instead of altering the commit snapshot.

`layout_cnodes()` assigns target LEB/offset locations without writing. It places lsave and ltab where possible, allocates empty LPT LEBs via `alloc_lpt_leb()`, updates ltab free/dirty accounting, and records new branch locations or root location.

`write_cnodes()` repeats the same allocation sequence with `realloc_lpt_leb()`, packs lsave/ltab/cnodes into `c->lpt_buf`, writes aligned chunks, clears `DIRTY_CNODE` and `COW_CNODE` with memory barriers, and advances `nhead_lnum:nhead_offs`.

For small LPT, `make_tree_dirty()` can force the whole tree dirty when space is low. For big LPT, `lpt_gc()` chooses a dirty LPT LEB and `lpt_gc_lnum()` scans its packed LPT nodes, marking still-current nodes dirty so they will be rewritten elsewhere.

Trivial GC marks LPT LEBs that contain only dirty+free space during start-commit and unmaps them after the master node has committed.

`ubifs_lpt_free()` releases write-only buffers, lsave, ltab commit copy, obsolete commit cnodes, loaded LPT tree nodes, heaps, dirty-index heap, ltab, and node buffers.

## Dependencies

Works with the packed LPT format and lazy lookup in `lpt.c`, lprops locking, category/lprops mutation, UBI LEB write/unmap/change, UBIFS authenticated hashing, debug infrastructure, and randomization hooks for lsave debug population.

## Research Notes

The start/end commit split relies on deterministic reallocation: end-commit must consume exactly the LEBs marked by start-commit. Space accounting is heavily asserted because LPT is designed never to run out of space. COW flag transitions and obsolete-node freeing are central to avoiding concurrent mutation of the commit snapshot.
