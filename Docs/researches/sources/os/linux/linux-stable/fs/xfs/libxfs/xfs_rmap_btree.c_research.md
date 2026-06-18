# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.c

## Scope

Implements per-AG reverse-map btree cursor operations, overlapping btree key behavior, buffer verification, in-memory rmap btree support, staged root commit, geometry calculations, reservation accounting, and cursor cache lifecycle.

## APIs And Entry Points

- Cursor and staging: `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`.
- Optional in-memory btree support: `xfs_rmapbt_mem_cursor`, `xfs_rmapbt_mem_init`.
- Geometry/reservation: `xfs_rmapbt_maxrecs`, `xfs_rmapbt_maxlevels_ondisk`, `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_size`, `xfs_rmapbt_max_size`, `xfs_rmapbt_calc_reserves`.
- Cache lifecycle: `xfs_rmapbt_init_cur_cache`, `xfs_rmapbt_destroy_cur_cache`.
- Exposes `xfs_rmapbt_buf_ops`, `xfs_rmapbt_ops`, and in-memory ops under `CONFIG_XFS_BTREE_IN_MEM`.

## Btree Operations

- Root state lives in AGF fields `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`.
- Btree blocks are allocated from the AGFL via `xfs_alloc_get_freelist`; freeing returns blocks to AGFL and marks them busy with discard skipped.
- Rmap btree geometry is overlapping: internal pointers carry low and high keys, so `key_len` is two rmap keys per pointer.
- Keys are ordered by startblock, owner, and offset key. The unwritten bit is masked out of key comparisons because it is a record attribute.
- High keys add `blockcount - 1` to physical startblock and, for file-data records, to logical offset.

## Verification

- `xfs_rmapbt_verify` checks magic, rmapbt feature enablement, v5 AG btree header fields, tree level bounds, and record counts.
- Online repair can validate against the larger of current and repair rmap levels.
- In-memory btrees use long pointers, filesystem-block headers, no CRC checking, and are allowed even when the on-disk rmap feature is not enabled.

## Geometry And Reservations

- Reflink filesystems compute maximum height based on possible extreme sharing, using available AG space rather than one record per AG block.
- Non-reflink filesystems compute height assuming one rmap record per AG block.
- Reserve calculation adds the larger of 1% of AG blocks or enough space for one block per rmap record, subtracting internal log blocks when the AG contains the log.

## Dependencies

- Uses generic and in-memory btree infrastructure, AGF logging, AG reservations, AGFL allocation/free, extent-busy tracking, perag cached AGF state, online repair state, buf verification, rmap offset packing helpers, and trace/error infrastructure.

## Invariants And Risks

- Rmapbt blocks come from AGFL, so freelist/refill ordering and rmapbt reservations are part of correctness.
- Unwritten must be ignored in key comparisons but preserved in records; mixing this up can make convert operations fail or duplicate keys.
- Overlapping btree high-key calculations must match query expectations for shared reflink data.
- Staged commit swaps only the root metadata; callers must clean up old blocks after commit.
