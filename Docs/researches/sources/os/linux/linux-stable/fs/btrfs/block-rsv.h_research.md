# File Research: sources/os/linux/linux-stable/fs/btrfs/block-rsv.h

## Purpose

`block-rsv.h` declares Btrfs metadata block reserve types, the `struct btrfs_block_rsv` layout, and APIs for initializing, adding, refilling, migrating, consuming, releasing, and querying metadata reservations.

## Main Types

- `enum btrfs_rsv_type` defines reserve classes:
  - `BTRFS_BLOCK_RSV_GLOBAL`
  - `BTRFS_BLOCK_RSV_DELALLOC`
  - `BTRFS_BLOCK_RSV_TRANS`
  - `BTRFS_BLOCK_RSV_CHUNK`
  - `BTRFS_BLOCK_RSV_REMAP`
  - `BTRFS_BLOCK_RSV_DELOPS`
  - `BTRFS_BLOCK_RSV_DELREFS`
  - `BTRFS_BLOCK_RSV_TREELOG`
  - `BTRFS_BLOCK_RSV_EMPTY`
  - `BTRFS_BLOCK_RSV_TEMP`
- `struct btrfs_block_rsv` contains:
  - `size`: desired reserve size.
  - `reserved`: currently reserved bytes.
  - `space_info`: backing metadata/system/remap/treelog space pool.
  - `lock`: protects reserve counters and flags.
  - `full`: fast fullness marker.
  - `failfast`: used by truncate/temp-style operations.
  - `type`: reserve type.
  - `qgroup_rsv_size` and `qgroup_rsv_reserved`: qgroup metadata reservation mirrors.

## Public API Surface

- Initialization/allocation:
  - `btrfs_init_block_rsv()`
  - `btrfs_init_root_block_rsv()`
  - `btrfs_alloc_block_rsv()`
  - `btrfs_init_metadata_block_rsv()`
  - `btrfs_free_block_rsv()`
- Reserving/checking/refilling:
  - `btrfs_block_rsv_add()`
  - `btrfs_block_rsv_check()`
  - `btrfs_block_rsv_refill()`
- Movement and consumption:
  - `btrfs_block_rsv_migrate()`
  - `btrfs_block_rsv_use_bytes()`
  - `btrfs_block_rsv_add_bytes()`
  - `btrfs_block_rsv_release()`
- Global/root integration:
  - `btrfs_update_global_block_rsv()`
  - `btrfs_init_global_block_rsv()`
  - `btrfs_release_global_block_rsv()`
  - `btrfs_use_block_rsv()`
  - `btrfs_unuse_block_rsv()`
- Truncate/free-space-cache guard:
  - `btrfs_check_trunc_cache_free_space()`

## Inline Helpers

- `btrfs_unuse_block_rsv()` adds one block back to a reserve without growing its target, then releases excess.
- `btrfs_block_rsv_full()` is a lockless/data-race-annotated fast path for fullness.
- `btrfs_block_rsv_reserved()` returns `reserved` under the spinlock to avoid KCSAN warnings.
- `btrfs_block_rsv_size()` returns `size` under the spinlock to avoid KCSAN warnings.

## Dependencies

The header forward-declares transaction, root, space-info, fs-info, and flush enum types. It depends on Linux integer, compiler, and spinlock definitions.

## Risks And Invariants

- Direct reads of `size`, `reserved`, and `full` can trigger data races unless using the provided helpers or holding `lock`.
- `qgroup_rsv_size/reserved` have different semantics from normal metadata reserve bytes and represent an upper bound for qgroup metadata demand.
- Callers must bind reserves to the correct `space_info`; migration/release logic assumes reserve space types are meaningful.
