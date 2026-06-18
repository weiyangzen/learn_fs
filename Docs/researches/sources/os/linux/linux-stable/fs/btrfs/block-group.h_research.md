# File Research: sources/os/linux/linux-stable/fs/btrfs/block-group.h

## Purpose

`block-group.h` declares the in-memory block-group model and public APIs for Btrfs block-group lookup, caching, allocation, accounting, reclaim, deletion, freezing, swap pins, size classes, and fully remapped block groups.

## Main Types

- `enum btrfs_disk_cache_state` tracks old free-space-cache persistence:
  - `BTRFS_DC_WRITTEN`
  - `BTRFS_DC_ERROR`
  - `BTRFS_DC_CLEAR`
  - `BTRFS_DC_SETUP`
- `enum btrfs_block_group_size_class` categorizes data block groups by allocation size:
  - none, small, medium, large.
- `enum btrfs_discard_state` tracks async discard passes over extents, bitmaps, reset cursor state, and fully remapped groups.
- `enum btrfs_chunk_alloc_enum` controls chunk allocation force:
  - no force, limited, force, force for extent allocation.
- `enum btrfs_block_group_flags` defines runtime flags such as removed, to-copy, relocating repair, chunk item inserted, active zone, zoned data relocation, free-space-tree needs/added, sequential zone, new block group, fully remapped, and stripe-removal pending.
- `enum btrfs_caching_type` tracks in-memory free-space cache progress.
- `struct btrfs_caching_control` represents async caching work with list linkage, mutex, wait queue, `btrfs_work`, target block group, progress counter, and reference count.
- `struct btrfs_block_group` is the central block-group state object.

## `struct btrfs_block_group` State

Important fields include:

- Identity and accounting:
  - `fs_info`, `inode`, `start`, `length`, `flags`, `global_root_id`
  - `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`
  - `remap_bytes`, `identity_remap_count`
  - committed mirrors: `last_used`, `last_remap_bytes`, `last_identity_remap_count`, `last_flags`
- Free-space cache and allocation:
  - bitmap thresholds
  - `cached`, `caching_ctl`
  - `free_space_ctl`
  - `cluster_list`
  - `data_rwsem`
  - `full_stripe_len`
  - `size_class`
- Tree/list membership:
  - rb-tree `cache_node`
  - RAID/profile list `list`
  - shared `bg_list` for unused/reclaim/deleted/new lists
  - `ro_list`, `discard_list`, `dirty_list`, `io_list`, `active_bg_list`
- Coordination:
  - `lock`
  - `refs`
  - `frozen`
  - `reservations`
  - `nocow_writers`
  - `free_space_lock`
  - `swap_extents`
- Zoned fields:
  - `alloc_offset`
  - `zone_unusable`
  - `zone_capacity`
  - `meta_write_pointer`
  - `physical_map`
  - `zone_finish_work`
  - `last_eb`
- Reclaim/discard:
  - `discard_index`
  - `discard_eligible_time`
  - `discard_cursor`
  - `discard_state`
  - `reclaim_mark`

## Inline Helpers

- `btrfs_block_group_end()` returns `start + length`.
- `btrfs_is_block_group_used()` checks `used`, `reserved`, `pinned`, or `remap_bytes` under `bg->lock`.
- `btrfs_is_block_group_data_only()` excludes mixed groups and selects true data groups.
- `btrfs_block_group_available_space()` subtracts used, pinned, reserved, super stripes, and zone-unusable bytes.
- `btrfs_data_alloc_profile()`, `btrfs_metadata_alloc_profile()`, and `btrfs_system_alloc_profile()` wrap `btrfs_get_alloc_profile()`.
- `btrfs_block_group_done()` tests cache completion/error with a memory barrier.

## Public API Surface

The header exposes APIs for:

- Lookup/lifetime:
  - `btrfs_lookup_first_block_group()`
  - `btrfs_lookup_block_group()`
  - `btrfs_next_block_group()`
  - `btrfs_get_block_group()`
  - `btrfs_put_block_group()`
- NOCOW/reservation waits:
  - `btrfs_inc_nocow_writers()`
  - `btrfs_dec_nocow_writers()`
  - `btrfs_wait_nocow_writers()`
  - `btrfs_dec_block_group_reservations()`
  - `btrfs_wait_block_group_reservations()`
- Free-space cache:
  - `btrfs_wait_block_group_cache_progress()`
  - `btrfs_cache_block_group()`
  - `btrfs_get_caching_control()`
  - `btrfs_add_new_free_space()`
- Block-group creation/deletion/reclaim:
  - `btrfs_start_trans_remove_block_group()`
  - `btrfs_remove_bg_from_sinfo()`
  - `btrfs_remove_block_group()`
  - `btrfs_delete_unused_bgs()`
  - `btrfs_mark_bg_unused()`
  - `btrfs_reclaim_block_groups()`
  - `btrfs_reclaim_bgs_work()`
  - `btrfs_reclaim_bgs()`
  - `btrfs_mark_bg_to_reclaim()`
  - `btrfs_read_block_groups()`
  - `btrfs_make_block_group()`
- Read-only/dirty/cache commit handling:
  - `btrfs_inc_block_group_ro()`
  - `btrfs_dec_block_group_ro()`
  - `btrfs_start_dirty_block_groups()`
  - `btrfs_write_dirty_block_groups()`
  - `btrfs_setup_space_cache()`
  - `btrfs_update_block_group()`
- Reservation and chunk allocation:
  - `btrfs_add_reserved_bytes()`
  - `btrfs_free_reserved_bytes()`
  - `btrfs_chunk_alloc()`
  - `btrfs_force_chunk_alloc()`
  - `check_system_chunk()`
  - `btrfs_reserve_chunk_metadata()`
  - `btrfs_get_alloc_profile()`
  - `btrfs_rmap_block()`
- Teardown:
  - `btrfs_put_block_group_cache()`
  - `btrfs_free_block_groups()`
- Freeze/swap/size-class/remap:
  - `btrfs_freeze_block_group()`
  - `btrfs_unfreeze_block_group()`
  - `btrfs_inc_block_group_swap_extents()`
  - `btrfs_dec_block_group_swap_extents()`
  - `btrfs_calc_block_group_size_class()`
  - `btrfs_use_block_group_size_class()`
  - `btrfs_block_group_should_use_size_class()`
  - `btrfs_mark_bg_fully_remapped()`
  - `btrfs_populate_fully_remapped_bgs_list()`

## Dependencies

The header depends on Linux synchronization/refcount/list/rbtree primitives, Btrfs free-space cache definitions, public Btrfs tree flags, and forward declarations for transaction, inode, chunk map, and fs-info objects.

## Risks And Invariants

- Several counters are protected by different locks. `used/reserved/pinned/remap_bytes/swap_extents` require `bg->lock`; list membership often requires fs-level list locks or `groups_sem`.
- `bg_list` is intentionally multiplexed across several lists, so code must not assume a block group can be on unused, reclaim, deleted, and new lists simultaneously.
- The `frozen` counter protects logical/physical reuse after deletion; it is not a general reference count.
- Zoned-only fields must be interpreted only when the filesystem is zoned.
- Size-class state is best-effort and valid only for eligible data-only non-zoned block groups.
