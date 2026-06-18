# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.c

This file is the common helper for online repair code that builds a replacement btree. It manages block reservations, fake-root staging, allocation hints, bulk-loader block claiming, commit cleanup, and cancellation cleanup.

Initialization:
- `xrep_newbt_init_ag` initializes an AG btree builder with owner info, allocation hint, reservation type, reservation list, bload dirty limit, and slack estimates.
- `xrep_newbt_init_inode` initializes an inode-fork btree builder with a fake ifork.
- `xrep_newbt_init_metadir_inode` initializes a metadata inode btree builder with bmbt owner info and regular block allocation semantics.
- `xrep_newbt_init_bare` initializes a builder without automatic reservations.

Slack policy:
- `xrep_newbt_estimate_slack` uses default bulk-load slack unless debug knobs override it.
- If free space is below 10 percent for the relevant scope, it tightens leaf/node slack to reduce repair space usage.

Reservation and allocation:
- `xrep_newbt_add_blocks` records a reserved extent, holds the perag, and schedules autoreap when allocated in the transaction.
- `xrep_newbt_add_extent` manually adds caller-supplied blocks without autoreap.
- `xrep_newbt_alloc_ag_blocks` allocates blocks within the current AG.
- `xrep_newbt_alloc_file_blocks` allocates file-based btree blocks across the filesystem.
- `xrep_newbt_alloc_blocks` selects AG vs file allocation based on whether `sc->ip` is set.

Commit and cancel:
- `xrep_newbt_free_extent` either commits autoreap for cancelled/unused allocations or cancels autoreap and frees unused tail blocks after a committed btree.
- `xrep_newbt_free` walks all reservations, logs deferred frees in bounded batches, frees perag references, and frees fake iforks.
- `xrep_newbt_commit` frees only unused reservation space after a successful btree commit.
- `xrep_newbt_cancel` rolls back all reserved blocks for an abandoned replacement tree.

Bulk loading:
- `xrep_newbt_claim_block` hands one reserved block to the btree bulk loader, advances `used`, rotates exhausted reservations, fills short or long btree pointers, and finishes deferred work to relog EFIs.
- `xrep_newbt_unused_blocks` reports unused reserved blocks.

Important invariants:
- AG btree allocation must remain in the scrubbed AG.
- File btree allocation validates hints against EOFS.
- `XREP_MAX_ITRUNCATE_EFIS` limits deferred free items before rolling/finishing deferred work.
- Reservations are protected with autoreap so failures do not leak blocks where possible.

Risks and edge cases:
- Filesystem shutdown skips block freeing and only cleans incore tracking.
- ENOSPC during allocation or claiming blocks cancels the staged tree.
- Metadir inode btree repair accepts higher ENOSPC risk because metadata reservations cannot be charged until commit.
