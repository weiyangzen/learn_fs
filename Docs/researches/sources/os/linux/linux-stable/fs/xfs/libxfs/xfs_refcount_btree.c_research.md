# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.c

## Scope

Implements the per-AG refcount btree cursor operations, buffer verification, btree geometry calculations, reserve accounting, staged-btree commit, and cursor slab cache lifecycle.

## APIs And Entry Points

- Cursor and staging: `xfs_refcountbt_init_cursor`, `xfs_refcountbt_commit_staged_btree`.
- Geometry/reservation: `xfs_refcountbt_maxrecs`, `xfs_refcountbt_maxlevels_ondisk`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`.
- Cache lifecycle: `xfs_refcountbt_init_cur_cache`, `xfs_refcountbt_destroy_cur_cache`.
- Exposes `xfs_refcountbt_buf_ops` and `xfs_refcountbt_ops`.

## Btree Operations

- Root state lives in AGF fields `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`.
- New btree blocks are allocated as metadata near the refcount btree target block with `XFS_RMAP_OINFO_REFC` ownership and `XFS_AG_RESV_METADATA`.
- Freed btree blocks decrement AGF block counts and are released through delayed extent freeing with refcount-btree rmap owner info.
- Record keys use encoded startblock. High keys are computed as `startblock + blockcount - 1`.
- Ordering is non-overlapping by encoded startblock; records are in order when one record’s end is less than or equal to the next start.

## Verification

- `xfs_refcountbt_verify` checks magic, reflink feature enablement, v5 AG btree header validity, tree level bounds, and block record counts.
- Online repair can temporarily validate against the larger of the current level and repair level.
- Read verification checks CRC first; write verification validates structure and updates CRC.

## Dependencies

- Uses generic btree, btree staging, allocation, AGF logging, rmap owner info, mount geometry, perag cached AGF state, online repair state, tracepoints, and health reporting.
- Depends on `xfs_refcount_encode_startblock` to build on-disk records from cursor state.

## Invariants And Risks

- Refcount btrees only exist on reflink filesystems.
- AGF root/level/block counters and perag cached levels must stay synchronized.
- Reserve calculations subtract internal log space from AG size because permanent log blocks cannot back future btree growth.
- Staged commits atomically swap in fake-root state; old tree cleanup is the caller’s responsibility.
