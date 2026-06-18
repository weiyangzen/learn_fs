# File Research: sources/os/linux/linux-stable/fs/ubifs/lpt_commit.c

## Summary
Implements commit-time handling for the UBIFS LPT: collecting dirty cnodes, laying out their new on-flash locations, writing them, managing LPT-area free/dirty accounting, performing LPT garbage collection, and freeing LPT resources.

## Key APIs
- `ubifs_lpt_start_commit()`.
- `ubifs_lpt_end_commit()`.
- `ubifs_lpt_post_commit()`.
- `ubifs_lpt_free()`.
- Debug/exported helpers: `dbg_check_ltab()`, `dbg_chk_lpt_free_spc()`, `dbg_chk_lpt_sz()`, `ubifs_dump_lpt_lebs()`.

## Important Behavior
Commit is split into start, end, and post-commit stages. Start-commit locks `lp_mutex`, validates LPT accounting under debug options, handles initial free-space checks, starts trivial GC, optionally dirties the entire tree for small LPT, populates `lsave` for big LPT, builds a circular `cnext` list of dirty cnodes, computes their new layout, calculates the LPT hash into the master node, and snapshots `ltab` into `ltab_cmt`.

`layout_cnodes()` assigns future locations to dirty pnodes/nnodes, ltab, and optional lsave without writing. `write_cnodes()` then repeats the same LEB allocation sequence using `realloc_lpt_leb()`, writes packed nodes to `lpt_buf`, clears `DIRTY_CNODE` and `COW_CNODE` with memory barriers, updates the LPT head, and writes the copied `ltab_cmt`.

For the big model, LPT GC scans an LPT LEB, identifies valid LPT nodes by type/CRC, and marks still-current nodes dirty so they are rewritten on the next commit; obsolete nodes are ignored. Trivial GC marks LPT LEBs containing only dirty/free bytes reusable after the master node is safely committed.

`ubifs_lpt_free()` releases write-only buffers first, then walks the partially materialized LPT tree and frees loaded nodes, heaps, ltab, and node buffers.

## Dependencies
Works tightly with `lpt.c` pack/unpack/lookup/COW routines, `lp_mutex`, lprops heaps/lists, UBI LEB I/O, master-node LPT hash fields, and UBIFS commit sequencing.

## Risks
Layout and write allocation must remain identical; mismatch is treated as fatal LPT space corruption. COW flags protect readers/writers during commit, so flag clearing order and memory barriers are important. Big-LPT GC assumes node CRC/type parsing can distinguish valid current nodes from stale data.
