# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.c

Implements the AG-local refcount btree adapter for the generic XFS btree layer. It defines cursor allocation, block allocation/freeing, key/record conversion, verifier callbacks, btree ordering functions, staged repair commit, maxlevel calculation, and AG reservation sizing.

Btree behavior:
- `xfs_refcountbt_ops` defines a short-pointer AG btree named `refcount`.
- Records are ordered by encoded startblock, where the CoW flag is part of the key.
- Keys consist of a single refcount startblock; high keys are computed as `start + blockcount - 1`.
- Record initialization encodes the refcount domain through `xfs_refcount_encode_startblock`.

AG metadata integration:
- Root and level are stored in `agf_refcount_root` and `agf_refcount_level`.
- Block count is stored in `agf_refcount_blocks`.
- `xfs_refcountbt_set_root`, allocation, freeing, and staged commit log the relevant AGF fields.
- Refcountbt block allocations use metadata reservation and rmap owner `XFS_RMAP_OINFO_REFC`.

Verification:
- `xfs_refcountbt_verify` checks magic, reflink feature availability, v5 AG btree header validity, tree level limits, and block geometry.
- Read verification checks CRC first, then structure.
- Write verification validates structure and updates CRC.
- Online repair may temporarily validate against a repair tree level if configured.

Sizing and reservations:
- `xfs_refcountbt_maxrecs` computes leaf/internal record capacity after header overhead.
- `xfs_refcountbt_maxlevels_ondisk` computes an on-disk upper bound using minimum CRC block size.
- `xfs_refcountbt_compute_maxlevels` disables levels when reflink is absent.
- `xfs_refcountbt_calc_reserves` reads AGF state and asks for enough space for worst-case refcountbt growth, excluding internal log blocks.

Lifecycle:
- `xfs_refcountbt_init_cursor` allocates and initializes a cursor with AG buffer and perag group hold.
- `xfs_refcountbt_commit_staged_btree` installs a rebuilt staged btree root into AGF.
- `xfs_refcountbt_init_cur_cache` and destroy manage the cursor slab cache.
