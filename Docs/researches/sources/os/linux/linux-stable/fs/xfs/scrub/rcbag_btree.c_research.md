# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.c

This file defines the in-memory btree implementation used by `rcbag.c`.

Btree key/record behavior:
- Keys are `(rbg_startblock, rbg_blockcount)`.
- Records add `rbg_refcount`.
- Key and record ordering sort first by startblock, then blockcount.
- Cursor record initialization copies all record fields.

Verifier:
- `rcbagbt_verify` checks magic, v5 long-block header, level bounds, and in-memory block record capacity.
- CRC checks are skipped for in-memory btrees to save time.

Btree ops:
- `rcbagbt_mem_ops` plugs into generic XFS in-memory btree support with xfbtree allocation/free/root operations and rcbag-specific comparison/record functions.
- `rcbagbt_mem_cursor` creates cursors from a kmem cache sized for the maximum possible height.
- `rcbagbt_mem_init` initializes an `xfbtree`.

Sizing/cache:
- `rcbagbt_maxrecs`, `rcbagbt_calc_size`, and `rcbagbt_maxlevels_possible` compute capacity and maximum height.
- `rcbagbt_init_cur_cache` and `rcbagbt_destroy_cur_cache` manage the cursor slab cache.

Record helpers:
- `rcbagbt_lookup_eq`
- `rcbagbt_get_rec`
- `rcbagbt_update`
- `rcbagbt_insert`

The implementation is compiled only when `CONFIG_XFS_BTREE_IN_MEM` support is available.
