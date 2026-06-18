# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.c

Implements reverse mapping btree mechanics for the generic XFS btree framework, including AG on-disk rmapbt and optional in-memory rmap btrees.

Key responsibilities:
- Defines AG rmap btree ops `xfs_rmapbt_ops`.
- Maintains AGF root, level, and block count fields for the rmap btree.
- Allocates/free rmapbt blocks from/to the AGFL, with busy extent handling and AG reservation accounting.
- Constructs low and high keys from records for an overlapping btree.
- Orders keys by physical startblock, owner, and packed offset with unwritten masked out.
- Verifies rmap btree buffers: magic, feature bit, v5 AG header, level bounds, and max records.
- Declares buffer ops `xfs_rmapbt_buf_ops`.
- Marks the btree geometry as overlapping via `XFS_BTGEO_OVERLAPPING`.
- Supports in-memory rmap btrees under `CONFIG_XFS_BTREE_IN_MEM`, including separate mem ops, buffer verification, cursor creation, and init.
- Supports staged btree commit for online repair.
- Computes max records, max levels, max size, and reservation requirements.
- Manages the rmap cursor slab cache.

Important functions:
- `xfs_rmapbt_init_cursor`
- `xfs_rmapbt_alloc_block`, `xfs_rmapbt_free_block`
- `xfs_rmapbt_init_key_from_rec`, `xfs_rmapbt_init_high_key_from_rec`
- `xfs_rmapbt_cmp_key_with_cur`, `xfs_rmapbt_cmp_two_keys`
- `xfs_rmapbt_verify`, read/write verifiers
- `xfs_rmapbt_mem_cursor`, `xfs_rmapbt_mem_init`
- `xfs_rmapbt_commit_staged_btree`
- `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_reserves`

Design notes:
- Internal nodes use two keys per pointer because rmap is an overlapping btree.
- On reflink filesystems, max-level calculation accounts for high sharing, where many owners can map one physical block.
- Reservation asks for the larger of 1% of the AG or max btree size.
