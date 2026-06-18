# File Research: sources/os/linux/linux/fs/ubifs/tnc_commit.c

Read completely: 1112 lines.

This file implements the TNC commit algorithm: selecting dirty znodes, assigning on-flash locations for rewritten index nodes, optionally writing into obsolete gaps, writing the new index, and finalizing clean/obsolete znode state.

Main entry points: `ubifs_tnc_start_commit` and `ubifs_tnc_end_commit`.

Index-node construction: `make_idx_node` serializes a dirty znode into an on-flash `UBIFS_IDX_NODE`, copies child keys/locations/hashes, prepares the node, calculates its hash, records old index position, updates the parent/root zbranch, adjusts calculated index size, clears dirty/COW flags, and decrements the dirty count.

In-the-gaps commit: `layout_leb_in_gaps` scans a dirty index LEB, determines which existing index nodes are still in use via `is_idx_node_in_use`, fills obsolete gaps with new index nodes using `fill_gap`, pads remaining space, updates lprops, and atomically changes the LEB. `layout_in_gaps` repeats this while insufficient empty LEBs are available, growing the `gap_lebs` array if index LEB count increases during allocation.

Empty-space layout: `layout_in_empty_space` places remaining dirty znodes into the index head or newly allocated empty index LEBs, updates parent/root positions, lprops, calculated index size, and debug expected index-head position without writing the index bytes yet.

Dirty znode selection: `find_first_dirty`, `find_next_dirty`, and `get_znodes_to_commit` build a circular `cnext` list of dirty znodes, set `COW_ZNODE` to freeze them against concurrent mutation, store commit-parent information, reset `alt`, and assert the count matches `dirty_zn_cnt`.

LEB allocation: `alloc_idx_lebs` estimates required empty LEBs and obtains them with `ubifs_find_free_leb_for_idx`; `free_unused_idx_lebs` and `free_idx_lebs` release excess allocations. Debug index checking can force an artificial `-ENOSPC` to exercise in-the-gaps layout.

Start commit: `ubifs_tnc_start_commit` checks TNC consistency, builds the commit znode list, allocates and lays out index locations, frees unused index LEBs, destroys the old-index RB-tree, returns the new root zbranch, saves dirty index LEB numbers, and updates budgeting state to treat the new index size as committed.

Write phase: `write_index` serializes index nodes to `c->cbuf`, writes them to the laid-out LEB offsets, updates hashes in both commit-parent and live-parent branches under `tnc_mutex`, and clears dirty before COW with memory barriers so concurrent dirtying sees a valid state.

End commit: `ubifs_tnc_end_commit` returns in-gap LEBs, writes index nodes, frees obsolete znodes, converts committed znodes to clean by updating clean counters, clears `cnext`, and frees allocated index-LEB arrays.

Important interactions: this file consumes dirty znode state prepared by `tnc.c`, uses `scan.c` for in-gap LEB scans, relies on lprops/find code for index LEB selection and accounting, and feeds the commit subsystem with the new root index location.

Reliability notes: the commit path maintains the invariant that a complete old index remains intact until the new index is safely written. Dirty and COW bit ordering in `write_index` is explicitly synchronized to prevent races with `dirty_cow_znode`.
