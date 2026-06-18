# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc_repair.c

This file repairs the inode allocation btrees by rebuilding both inobt and finobt from reverse mapping records and inode cluster contents.

Core repair model:
- Requires rmapbt support.
- Walks rmap records for `OWN_INODES` and `OWN_INOBT`.
- Reconstructs inode records from inode cluster buffers.
- Bulk-loads new inobt and finobt trees.
- Commits new roots to the AGI and reaps old btree blocks.

Key state:
- `struct xrep_ibt` holds the current reconstructed inode record, two `xrep_newbt` builders, a bitmap of old inode btree blocks, an `xfarray` of reconstructed records, counters, and array cursor state.

Record reconstruction:
- `xrep_ibt_record_inode_blocks` validates inode rmap extents and processes each cluster.
- `xrep_ibt_process_cluster` directly maps inode cluster buffers without using the damaged inobt.
- `xrep_ibt_cluster_record` builds inobt records, computes hole/free masks, counts inodes, and tracks finobt record needs.
- `xrep_ibt_check_ifree` determines inode in-use state from incore allocation state or on-disk dinode mode.

Validation:
- `xrep_ibt_check_inode_ext` checks AG extent validity, cluster alignment, sparse inode alignment, valid inode number range, and absence from free-space btrees.
- `xrep_ibt_check_overlap` ensures reconstructed records are ordered and non-overlapping.

Tree rebuild:
- `xrep_ibt_build_new_trees` stages fake roots, computes bload geometry, reserves blocks, bulk-loads inobt and optional finobt, commits roots into AGI, resets AGI counters, commits new reservations, and rolls the AG transaction.
- `xrep_ibt_get_records` feeds all records to inobt.
- `xrep_fibt_get_records` feeds only records with free inodes to finobt.
- `xrep_ibt_remove_old_trees` reaps old inode btree blocks and requests per-AG reservation reset when needed.

Public entry points:
- `xrep_iallocbt` rebuilds both inode btrees and sets `sc->sick_mask` to cover both inobt and finobt.
- `xrep_revalidate_iallocbt` reruns scrub for inobt and, if enabled, finobt after repair.

Important invariants:
- Repair locks AGI through scrub setup, preventing concurrent inode allocation/free changes.
- Both trees are rebuilt together because they share rmap ownership and record source data.
- Old btrees become inaccessible only after staged roots are committed.

Risks and edge cases:
- ENOSPC can occur while reserving replacement btree blocks.
- If finobt revalidation loses its cursor, repair is marked incomplete.
- Bad rmap data prevents repair because rmap is the source of truth.
