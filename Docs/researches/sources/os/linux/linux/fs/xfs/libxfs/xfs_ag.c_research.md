# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.c

Implements XFS allocation-group lifecycle, geometry calculation, grow/shrink support, and new AG header initialization.

Key behavior:
- `xfs_initialize_perag_data` reads every AGF/AGI to rebuild incore superblock counters for allocated/free inodes and free blocks.
- Detects impossible summary counts, marks filesystem counters sick, and fails mount with `-EFSCORRUPTED`.
- Allocates, inserts, and frees per-AG structures through generic `xfs_group` helpers.
- Computes AG block counts, including shorter final AGs.
- Computes valid AG inode ranges after static AG metadata and inode-cluster alignment.
- Updates the previous tail AG geometry during growfs recovery.
- Initializes new per-AG structures with kernel-only inode-cache and blockgc state.
- Prepares uncached buffers for new AG headers during growfs.
- Initializes:
  - secondary superblocks with `sb_inprogress`.
  - AGF headers and free-space counters.
  - AGFL blocks and null entries.
  - AGI headers and unlinked-inode buckets.
  - free-space btree roots.
  - inode btree roots.
  - rmap/refcount roots when enabled.
- Builds initial free-space records while excluding AG headers and internal log space.
- Builds initial rmap records for static metadata, btree roots, refcount root, and internal log.
- Implements `xfs_ag_shrink_space`:
  - validates tail AG state.
  - checks inode allocation constraints.
  - disables/reinitializes per-AG reservations.
  - allocates the to-be-removed tail range exactly from free space.
  - updates AGI/AGF lengths and perag geometry.
  - handles reservation rollback and shutdown on unrecoverable reservation errors.
- Implements `xfs_growfs_compute_deltas` to normalize requested data-block count into AG count and delta.
- Implements `xfs_ag_extend_space`:
  - extends AGI/AGF length.
  - frees newly added space into rmap and free-space btrees.
  - updates perag geometry.
- Implements `xfs_ag_get_geometry` for reporting AG length, inode counts, free blocks, and health.

Important interactions:
- Depends on AGF/AGI readers from allocation and inode allocation code.
- Uses rmap and free-space allocation code to materialize grow/shrink changes.
- Per-AG reservations must be reestablished around shrink operations.
- New AG initialization coordinates superblock, AG headers, free-space btrees, inode btrees, rmapbt, and refcountbt.
