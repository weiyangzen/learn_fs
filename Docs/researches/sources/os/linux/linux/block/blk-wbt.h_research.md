# File Research: sources/os/linux/linux/block/blk-wbt.h

## Scope

This header exposes the small internal interface for writeback throttling to queue registration and sysfs code.

## APIs

- With `CONFIG_BLK_WBT`, it declares:
  - `wbt_init_enable_default()`
  - `wbt_disable_default()`
  - `wbt_enable_default()`
  - `wbt_get_min_lat()`
  - `wbt_disabled()`
  - `wbt_set_lat()`
- Without `CONFIG_BLK_WBT`, default enable/disable functions compile to no-ops. The query/set declarations are omitted because their callers are guarded by `CONFIG_BLK_WBT`.

## Dependencies and Invariants

- Operates on `gendisk` and `request_queue`.
- The header intentionally hides `struct rq_wb`; callers interact only through disk/queue-level helpers.
