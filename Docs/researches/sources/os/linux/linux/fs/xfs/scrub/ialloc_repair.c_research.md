# File Research: sources/os/linux/linux/fs/xfs/scrub/ialloc_repair.c

Rebuilds both inode allocation btrees for an AG from reverse mapping data. The repair is coupled because inobt and finobt share the same rmap owner and are easier to reconstruct together from inode cluster state.

Main flow:
- `struct xrep_ibt` tracks the record under construction, new inobt/finobt staging state, old btree blocks, reconstructed records in an `xfarray`, inode/free counts, finobt record count, and array cursor state.
- `xrep_ibt_check_ifree` determines whether an inode is in use from icache or disk dinode state.
- `xrep_ibt_cluster_record` builds/updates the reconstructed inobt record for an inode cluster, maintaining count, holemask, and freemask.
- `xrep_ibt_process_cluster` reads an inode cluster buffer directly and processes each possible inobt record covered by the cluster.
- `xrep_ibt_check_inode_ext` validates rmap-owned inode extents for AG bounds, cluster alignment, sparse/non-sparse alignment, inode-number validity, and not-free-space status.
- `xrep_ibt_walk_rmap` collects old inode btree blocks (`OWN_INOBT`) and inode cluster extents (`OWN_INODES`).
- `xrep_ibt_find_inodes` walks all AG rmaps and stashes the final reconstructed record.
- `xrep_ibt_reset_counters` updates AGI inode/free counters and reinitializes per-AG state.
- `xrep_ibt_get_records` and `xrep_fibt_get_records` feed reconstructed inobt and finobt records to the btree bulk loader.
- `xrep_ibt_build_new_trees` checks record overlap, stages new fake-root btrees, computes geometry, reserves blocks, bulk-loads records, commits new roots to AGI, resets counters, and commits reservations.
- `xrep_ibt_remove_old_trees` reaps old inode-btree blocks and requests per-AG reservation reset when needed.
- `xrep_iallocbt` requires rmapbt, allocates repair state, expands `sick_mask` to both inobt and finobt, builds records, installs new trees, and reaps old trees.
- `xrep_revalidate_iallocbt` temporarily changes scrub type to re-scrub inobt and finobt in the correct cross-reference direction.

Key invariants:
- Repair depends on rmapbt; without rmap ownership data it returns `-EOPNOTSUPP`.
- AGI locking protects against concurrent inode allocation/free while rebuilding.
- Records are collected in increasing AG inode order and checked for overlap before loading.
- Old trees are not reaped until new roots have been committed.
