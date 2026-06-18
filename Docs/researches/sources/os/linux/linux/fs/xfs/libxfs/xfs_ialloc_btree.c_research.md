# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.c

## Purpose

`xfs_ialloc_btree.c` implements btree operations for the inode allocation btree (`inobt`) and free inode btree (`finobt`). It supplies cursor constructors, btree operation tables, block allocation/freeing, verifiers, record/key helpers, staged root commit, capacity calculations, reserve accounting, and cursor cache lifecycle.

## Main Content

- Cursor/cache state:
  - Static `xfs_inobt_cur_cache`.
  - `xfs_inobt_init_cur_cache` and `xfs_inobt_destroy_cur_cache`.
- Btree min/max record helpers:
  - `xfs_inobt_get_minrecs`.
  - `xfs_inobt_get_maxrecs`.
  - `xfs_inobt_maxrecs`.
- Cursor duplication:
  - `xfs_inobt_dup_cursor`.
  - `xfs_finobt_dup_cursor`.
- Root updates:
  - `xfs_inobt_set_root` updates `agi_root` and `agi_level`.
  - `xfs_finobt_set_root` updates `agi_free_root` and `agi_free_level`.
- Btree block count tracking:
  - `xfs_inobt_mod_blockcount` updates `agi_iblocks` or `agi_fblocks` when the inobtcount feature is enabled.
- Block allocation/freeing:
  - `__xfs_inobt_alloc_block` allocates one AG block near the requested start with inode-btree rmap ownership.
  - `xfs_inobt_alloc_block` uses no AG reservation.
  - `xfs_finobt_alloc_block` uses metadata reservation unless disabled.
  - Matching free helpers queue blocks for deferred freeing and adjust block counts.
- Record/key/pointer initialization and comparison:
  - Key initialization from record and high key from record.
  - Record initialization from cursor, respecting sparse inode on-disk format.
  - Root pointer initialization from AGI root fields.
  - Key comparisons, key ordering, record ordering, and contiguity.
- Verification:
  - `xfs_inobt_verify` checks magic, V5 AG btree header, level bounds, and record limits.
  - Read/write verifiers validate CRC and structure, trace corruption, and update CRCs.
  - Buffer ops for inobt and finobt specify distinct magic values and names.
- Btree ops tables:
  - `xfs_inobt_ops`.
  - `xfs_finobt_ops`.
  - Both are AG btrees with short pointers and inode record/key sizes, but different roots, allocation reservation behavior, stats offsets, and sickness masks.
- Cursor constructors:
  - `xfs_inobt_init_cursor`.
  - `xfs_finobt_init_cursor`.
  - Both allocate cursors, hold the per-AG group, attach AGI buffer, and set current btree levels from AGI.
- Staged btree commit:
  - `xfs_inobt_commit_staged_btree` installs fake-root state into AGI root/level/blockcount fields and commits the staged btree root.
- Capacity/height calculations:
  - `xfs_inobt_block_maxrecs`.
  - On-disk max level calculations for inobt and finobt.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Sparse record helpers:
  - `xfs_inobt_irec_to_allocmask` expands a sparse record holemask into a per-inode physical allocation bitmap.
  - `xfs_inobt_rec_check_count` validates `ir_count` against the allocation bitmap in debug/warn builds.
- Reservation accounting:
  - `xfs_inobt_max_size` estimates worst-case inobt size per AG.
  - `xfs_finobt_count_blocks` counts blocks by walking the tree.
  - `xfs_finobt_read_blocks` reads `agi_fblocks` when available.
  - `xfs_finobt_calc_reserves` calculates finobt reservation ask/used.
  - `xfs_iallocbt_calc_size` wraps generic btree size calculation.

## Key Interfaces and Invariants

- Inobt and finobt share the same record format but have separate roots and magic numbers.
- Finobt uses metadata reservation unless `m_finobt_nores` disables it.
- Record ordering requires non-overlapping inode chunks: one record’s start plus `XFS_INODES_PER_CHUNK` must not exceed the next record’s start.
- V5 filesystems require AG btree header verification and CRC updates.
- Staged btree commit must update the correct AGI fields and optionally inobtcount block counters.

## Dependencies

Relies on btree core, staged btree infrastructure, AGI logging from `xfs_ialloc.c`, inode record formats from `xfs_format.h`, group references from `xfs_group`, allocation/freeing, rmap ownership constants, and health sickness masks.
