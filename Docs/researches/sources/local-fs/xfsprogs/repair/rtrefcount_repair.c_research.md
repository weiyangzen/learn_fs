# File Research: sources/local-fs/xfsprogs/repair/rtrefcount_repair.c

Rebuilds the realtime refcount btree for a realtime group from computed repair-time refcount records.

Key structure:
- `struct xrep_rtrefc`: holds slab cursor, staged inode fork bulkload state, repair context, rtgroup, and estimated free-data-block budget.

Core flow:
- `populate_rtgroup_refcountbt` opens a transaction for the rtgroup refcount inode and calls `xrep_rtrefc_build_new_tree`.
- `xrep_rtrefc_build_new_tree` stages a new metadata btree fork, bulkloads records, commits the staged root, updates inode counters, commits bulkload accounting, and rolls the transaction.
- `xrep_rtrefc_btree_load` computes btree geometry from `refcount_record_count`, reserves transaction space, allocates file blocks, initializes a refcount slab cursor, and calls libxfs bulkload.
- `xrep_rtrefc_get_records` feeds `xfs_refcount_irec` records from the slab cursor into btree blocks.
- `xrep_rtrefc_claim_block` delegates new btree block ownership to the bulkload layer.
- `xrep_rtrefc_iroot_size` calculates staged in-core root size for rtrefcount format.

Important behavior:
- No work is done unless realtime reflink is enabled.
- The new fork is explicitly marked `XFS_DINODE_FMT_META_BTREE`.
- Quota updates are unnecessary for these metadata inodes.
- On error, staged bulkload state is canceled and the transaction is canceled by the caller.
