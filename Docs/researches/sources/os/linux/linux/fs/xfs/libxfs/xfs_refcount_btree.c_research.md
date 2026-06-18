# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.c

Implements the AG refcount btree integration with the generic XFS btree framework. This file handles cursor setup, AGF root fields, block allocation/freeing, key construction, verifier callbacks, max-level calculations, staged repair commit, and reservation sizing.

Key responsibilities:
- Defines `xfs_refcountbt_ops` for the generic btree layer.
- Allocates refcount btree blocks from metadata reservation space near the refcount btree area, using owner info `XFS_RMAP_OINFO_REFC`.
- Updates AGF fields: `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`.
- Builds low/high keys from records; the high key is `startblock + blockcount - 1`.
- Encodes refcount domain into record keys via `xfs_refcount_encode_startblock`.
- Verifies refcount btree blocks: magic, reflink feature, v5 AG block header, level bounds, and record capacity.
- Provides buffer ops `xfs_refcountbt_buf_ops`.
- Supports online repair staging through `xfs_refcountbt_commit_staged_btree`.
- Computes max records, max levels, max size, and AG reservation requirements.
- Manages the cursor slab cache.

Important functions:
- `xfs_refcountbt_init_cursor`
- `xfs_refcountbt_alloc_block`, `xfs_refcountbt_free_block`
- `xfs_refcountbt_verify`, read/write verifiers
- `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`
- `xfs_refcountbt_calc_reserves`
- `xfs_refcountbt_commit_staged_btree`

Design notes:
- This file is about btree mechanics, not refcount semantics; semantic mutations live in `xfs_refcount.c`.
- It refuses verification if reflink is not enabled.
