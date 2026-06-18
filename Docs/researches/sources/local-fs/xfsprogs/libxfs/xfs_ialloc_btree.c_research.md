# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.c

## Purpose
Implements inode allocation btree and free inode btree cursor operations, block allocation/freeing, record/key callbacks, buffer verifiers, staged btree commit, record capacity calculations, sparse inode allocation mask conversion, finobt reserve calculation, and cursor cache lifecycle.

## Main Functional Areas
- Cursor operation callbacks:
  - Min/max records derive from mount inode geometry.
  - Duplicate cursor callbacks recreate inobt or finobt cursors for the same perag, transaction, and AGI buffer.
  - Root setters update AGI root/level fields for inobt or finobt and log AGI fields.
  - Key/record initializers and comparators operate on `ir_startino`.
  - Record ordering requires each inode chunk start to be at least `XFS_INODES_PER_CHUNK` after the prior record.
- Btree block accounting:
  - `xfs_inobt_mod_blockcount` updates AGI `agi_iblocks` or `agi_fblocks` when inobtcounts are enabled.
- Block allocation/freeing:
  - Inobt alloc/free uses normal AG reservation.
  - Finobt alloc/free uses metadata reservation unless `m_finobt_nores` is set.
  - Allocations request one block near the provided start block and tag reverse mapping owner as inobt.
  - Frees defer extent freeing through transaction infrastructure.
- Verification:
  - `xfs_inobt_verify` validates magic, v5 AG btree header, level bounds, and record capacity.
  - Read verifier checks CRC then structure; write verifier checks structure then updates CRC.
  - Shared read/write verifier logic supports both inobt and finobt through separate `xfs_buf_ops`.
- Btree ops tables:
  - `xfs_inobt_ops` and `xfs_finobt_ops` wire generic btree code to inode-specific callbacks, stats, buffer ops, and health masks (`XFS_SICK_AG_INOBT`, `XFS_SICK_AG_FINOBT`).
- Cursor initialization:
  - `xfs_inobt_init_cursor` and `xfs_finobt_init_cursor` allocate generic btree cursors, hold the perag group, attach AGI buffer, and set levels from AGI when available.
- Staged btree commit:
  - `xfs_inobt_commit_staged_btree` installs staged fake roots into AGI for inobt or finobt and logs root/level/block-count fields.
- Sizing:
  - `xfs_inobt_maxrecs` computes records per btree block after subtracting header length.
  - `xfs_iallocbt_maxlevels_ondisk` computes the maximum possible height of inobt/finobt for ondisk constraints.
  - `xfs_iallocbt_calc_size` estimates blocks needed for a given number of records.
- Sparse inode helpers:
  - `xfs_inobt_irec_to_allocmask` expands sparse record holemask into a per-inode physical allocation bitmap.
  - `xfs_inobt_rec_check_count` debug-validates `ir_count` against the expanded allocation mask.
- Finobt reservations:
  - `xfs_finobt_calc_reserves` reads or counts finobt blocks and adds maximum theoretical reservation ask plus actual used blocks.
  - Uses `agi_fblocks` when inobtcounts are available, otherwise walks the btree.
- Cursor cache:
  - `xfs_inobt_init_cur_cache` creates a kmem cache sized for maximum inode btree levels.
  - `xfs_inobt_destroy_cur_cache` destroys it.

## Dependencies and Integration
- Uses generic btree framework, staged btree framework, allocation APIs, reverse mapping owner info, AGI logging from `xfs_ialloc.c`, perag/group wrappers, health masks, and inode geometry.
- Exports buffer ops used when reading inobt/finobt blocks.
- Provides cursor constructors consumed by inode allocation/freeing, scrub, repair, and btree rebuild code.

## Invariants
- Inobt and finobt share record format but use different roots, levels, stats, reservations, and health masks.
- Cursor `bc_group` holds a passive reference to the perag group.
- V5 btree blocks require CRC/header verification; level must be less than inode geometry maxlevels.
- Inobt block counters are updated only when feature support exists.
- Sparse holemask zero bits represent physically allocated inode subranges after inversion/expansion.

## Notable Risks
- Any mismatch between AGI roots/levels/block counters and actual btree structure can corrupt inode allocation.
- Finobt reservation behavior depends on `m_finobt_nores`; incorrect setting can affect metadata reservation accounting.
- Staged btree commits require callers to invalidate/free old blocks separately, as noted by comments.
