# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.h

## Role
Declares the refcount-bag in-memory btree format and helper functions.

## Format
- `RCBAG_MAGIC` identifies in-memory refcount bag btree blocks.
- `struct rcbag_key` indexes records by start block and block count.
- `struct rcbag_rec` stores start block, block count, and accumulated refcount.
- Address macros compute record, key, and pointer locations in btree blocks.

## API
- Geometry helpers: `rcbagbt_maxrecs`, `rcbagbt_calc_size`, `rcbagbt_maxlevels_possible`.
- Cache lifecycle: `rcbagbt_init_cur_cache`, `rcbagbt_destroy_cur_cache`.
- Memory btree setup: `rcbagbt_mem_cursor`, `rcbagbt_mem_init`.
- Record operations: lookup, get, update, insert.

## Build Guards
When in-memory btrees are disabled, init/destroy degrade to no-op/success macros.
