# File Research: sources/local-fs/xfsprogs/repair/rcbag_btree.c

## Role

`rcbag_btree.c` defines the in-memory btree implementation backing `rcbag.c`. It adapts libxfs btree operations to fixed-size refcount bag records keyed by start block, block count, and inode owner.

## Core Behavior

- Defines key/record initialization, key comparison, ordering checks, and record ordering.
- Verifies in-memory btree blocks with `RCBAG_MAGIC`, v5 btree headers, max levels, and max records.
- Provides `rcbagbt_mem_ops`, an `XFS_BTREE_TYPE_MEM` operation table using xfbtree allocation/free/root helpers.
- `rcbagbt_mem_cursor()` allocates cursors from a dedicated kmem cache.
- `rcbagbt_mem_init()` initializes an xfbtree over an xmbuf buffer target.
- `rcbagbt_maxrecs()`, `rcbagbt_calc_size()`, and `rcbagbt_maxlevels_possible()` size the tree.
- Lookup/get/update/insert helpers translate between rmap records, rcbag records, and libxfs btree cursors.

## Dependencies

It depends on libxfs btree internals, xfbtree memory btrees, xfs buffer verification, kmem cache allocation, and `rcbag_btree.h`.

## Risk Areas

- The btree ordering contract must match `rcbag.c` expectations exactly.
- The cursor cache must be initialized and destroyed by repair startup/shutdown.
- CRC checks are skipped for speed, so structural verification is the main guard for this in-memory tree.
