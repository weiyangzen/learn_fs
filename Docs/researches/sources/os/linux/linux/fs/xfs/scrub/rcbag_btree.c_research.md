# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.c

## Role
Defines the in-memory btree implementation backing `rcbag`.

## Btree Format
- Records contain start block, block count, and refcount.
- Keys contain start block and block count.
- Ordering is lexicographic by start block then block count.
- Uses XFS in-memory btree (`xfbtree`) operations and buffer verification.

## Cursor and Ops
- `rcbagbt_mem_ops` supplies XFS btree callbacks for key/record conversion, comparison, ordering, block allocation, and root management.
- `rcbagbt_mem_cursor` allocates a memory btree cursor from a slab cache.
- `rcbagbt_mem_init` initializes the in-memory btree.

## Geometry
- `rcbagbt_maxrecs`, `rcbagbt_maxlevels_possible`, and `rcbagbt_calc_size` compute btree capacity and space needs.
- Verifiers use `RCBAG_MAGIC` and memory btree block checks.

## Record Helpers
- `rcbagbt_lookup_eq` positions by rmap start/length.
- `rcbagbt_get_rec`, `rcbagbt_update`, and `rcbagbt_insert` wrap generic XFS btree record operations.

## Lifecycle
- `rcbagbt_init_cur_cache` and `rcbagbt_destroy_cur_cache` manage the cursor slab cache.
