# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.c

Implements the AG reverse mapping btree adapter for the generic btree layer, plus optional in-memory rmap btree support. The rmap btree is an overlapping btree ordered by physical block, owner, and key-significant offset flags.

Btree model:
- `xfs_rmapbt_ops` defines an AG btree named `rmap` with `XFS_BTGEO_OVERLAPPING`.
- Internal nodes store low and high keys per pointer.
- Key ordering uses startblock, owner, and offset with the unwritten bit masked out.
- High-key construction extends both physical startblock and file offset for inode data/attr mappings; metadata and bmbt records do not advance offset.

AG integration:
- Root, level, and block count live in AGF fields `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`.
- Rmapbt blocks are allocated from the AGFL via `xfs_alloc_get_freelist`, not normal free-space allocation.
- Freeing returns blocks to AGFL and records busy extents with discard skipping.
- Reservation accounting uses `XFS_AG_RESV_RMAPBT`.

Verification:
- `xfs_rmapbt_verify` checks magic, rmapbt feature availability, v5 AG btree header, tree level limits, and block geometry.
- Read verification checks CRC then structure; write verification validates and updates CRC.
- Repair builds can temporarily validate against repair rmap levels.

In-memory rmap btree support:
- Under `CONFIG_XFS_BTREE_IN_MEM`, defines memory btree block capacity, verification, buffer ops, and `xfs_rmapbt_mem_ops`.
- `xfs_rmapbt_mem_cursor` creates cursors for in-memory rmap btrees.
- `xfs_rmapbt_mem_init` initializes an xfbtree with an AG owner.
- In-memory maxlevel calculation is folded into on-disk maxlevel bounds.

Sizing and reservations:
- `xfs_rmapbt_maxrecs` computes per-block record/key capacity.
- `xfs_rmapbt_maxlevels_ondisk` accounts for worst-case reflink sharing and optional in-memory tree height.
- `xfs_rmapbt_compute_maxlevels` uses space-to-height for reflink filesystems and one-record-per-block assumptions otherwise.
- `xfs_rmapbt_calc_reserves` reserves the larger of 1% of AG blocks or calculated max btree size, excluding internal log blocks.

Lifecycle:
- `xfs_rmapbt_init_cursor` creates AG cursors with perag group holds.
- `xfs_rmapbt_commit_staged_btree` installs staged repair roots into AGF.
- Cache lifecycle is handled by `xfs_rmapbt_init_cur_cache` and `xfs_rmapbt_destroy_cur_cache`.
