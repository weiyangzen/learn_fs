# File Research: sources/os/linux/linux/fs/btrfs/block-group.h

## Scope And Role

`block-group.h` declares the public data structures, enums, helper functions, and APIs for Btrfs block-group management. It is the interface consumed by allocation, free-space, transaction, relocation, discard, zoned, and chunk/device mapping code.

The core type is `struct btrfs_block_group`, which represents one logical chunk/block-group and stores accounting, free-space cache state, runtime flags, transaction lists, discard/reclaim state, zoned state, and allocation size-class information.

## Main Enums

`enum btrfs_disk_cache_state` tracks old space-cache write state:
- `BTRFS_DC_WRITTEN`
- `BTRFS_DC_ERROR`
- `BTRFS_DC_CLEAR`
- `BTRFS_DC_SETUP`

`enum btrfs_block_group_size_class` groups data allocations into:
- none
- small: `0 < size <= 128K`
- medium: `128K < size <= 8M`
- large: `8M < size < BG_LENGTH`

`enum btrfs_discard_state` tracks async discard passes over extent and bitmap free-space representations, plus reset/remap states.

`enum btrfs_chunk_alloc_enum` controls chunk allocation pressure:
- no force
- limited
- force
- force for extent allocation

`enum btrfs_block_group_flags` defines runtime bit positions for state such as removed, to-copy, chunk item inserted, zone active, new, fully remapped, stripe removal pending, and free-space-tree update needs.

`enum btrfs_caching_type` tracks free-space cache lifecycle:
- no caching
- started
- finished
- error

## Core Structures

`struct btrfs_caching_control` owns async free-space caching work. It has a list node, mutex, waitqueue, work item, associated block group, progress counter, and refcount.

`CACHING_CTL_WAKE_UP` is `SZ_2M`, the free-space progress threshold used to wake allocation waiters during caching.

`struct btrfs_block_group` includes:

- Identity and range: `fs_info`, `inode`, `start`, `length`, `global_root_id`.
- Accounting: `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `identity_remap_count`, last-committed snapshots, and bitmap thresholds.
- Profile/type: `flags`, `full_stripe_len`, `space_info`.
- State: `runtime_flags`, `ro`, `disk_cache_state`, `cached`, `caching_ctl`.
- Free-space: `free_space_ctl`, `io_ctl`, `free_space_lock`, bitmap usage booleans.
- Index/list membership: rb tree node, raid-type list, cluster list, bg list, read-only list, dirty/io lists, discard list, active-zoned list.
- Lifetime/synchronization: refcount, spinlock, data rwsem, frozen counter, reservation and nocow-writer atomics.
- Discard/reclaim: discard index/time/cursor/state and `reclaim_mark`.
- Zoned fields: allocation offset, unusable/capacity, metadata write pointer, physical map, zone finish work, last extent buffer.
- Allocation policy: `size_class`.

## Inline Helpers

`btrfs_block_group_end()` returns `start + length`.

`btrfs_is_block_group_used()` checks `used`, `reserved`, `pinned`, and `remap_bytes` under the block-group lock.

`btrfs_is_block_group_data_only()` returns true only for non-mixed data groups.

`btrfs_block_group_available_space()` returns length minus used, pinned, reserved, super bytes, and zone-unusable bytes under lock.

`btrfs_data_alloc_profile()`, `btrfs_metadata_alloc_profile()`, and `btrfs_system_alloc_profile()` wrap `btrfs_get_alloc_profile()` with the corresponding block-group type.

`btrfs_block_group_done()` uses a memory barrier and checks whether caching finished or errored.

## Public API Surface

Lookup/lifetime:
- `btrfs_lookup_first_block_group()`
- `btrfs_lookup_block_group()`
- `btrfs_next_block_group()`
- `btrfs_get_block_group()`
- `btrfs_put_block_group()`

Reservation and NOCOW synchronization:
- `btrfs_dec_block_group_reservations()`
- `btrfs_wait_block_group_reservations()`
- `btrfs_inc_nocow_writers()`
- `btrfs_dec_nocow_writers()`
- `btrfs_wait_nocow_writers()`

Caching/free-space:
- `btrfs_get_caching_control()`
- `btrfs_wait_block_group_cache_progress()`
- `btrfs_cache_block_group()`
- `btrfs_add_new_free_space()`

Lifecycle:
- `btrfs_start_trans_remove_block_group()`
- `btrfs_remove_bg_from_sinfo()`
- `btrfs_remove_block_group()`
- `btrfs_delete_unused_bgs()`
- `btrfs_mark_bg_unused()`
- `btrfs_read_block_groups()`
- `btrfs_make_block_group()`
- `btrfs_create_pending_block_groups()`
- `btrfs_put_block_group_cache()`
- `btrfs_free_block_groups()`

Reclaim:
- `btrfs_reclaim_block_groups()`
- `btrfs_reclaim_bgs_work()`
- `btrfs_reclaim_bgs()`
- `btrfs_mark_bg_to_reclaim()`

Read-only and dirty updates:
- `btrfs_inc_block_group_ro()`
- `btrfs_dec_block_group_ro()`
- `btrfs_start_dirty_block_groups()`
- `btrfs_write_dirty_block_groups()`
- `btrfs_setup_space_cache()`
- `btrfs_update_block_group()`

Allocation/chunk:
- `btrfs_add_reserved_bytes()`
- `btrfs_free_reserved_bytes()`
- `btrfs_chunk_alloc()`
- `btrfs_force_chunk_alloc()`
- `check_system_chunk()`
- `btrfs_reserve_chunk_metadata()`
- `btrfs_get_alloc_profile()`
- `btrfs_rmap_block()`

Special states:
- `btrfs_freeze_block_group()`
- `btrfs_unfreeze_block_group()`
- `btrfs_inc_block_group_swap_extents()`
- `btrfs_dec_block_group_swap_extents()`
- `btrfs_calc_block_group_size_class()`
- `btrfs_use_block_group_size_class()`
- `btrfs_block_group_should_use_size_class()`
- `btrfs_mark_bg_fully_remapped()`
- `btrfs_populate_fully_remapped_bgs_list()`

## Integration Points

This header includes `free-space-cache.h`, Linux list/rbtree/refcount/wait/rwsem primitives, and Btrfs UAPI tree definitions.

It is tightly coupled with:
- `space-info` accounting.
- Free-space cache/tree code.
- Chunk mapping and device extent code.
- Transaction dirty block-group handling.
- Discard and reclaim workers.
- Zoned block allocation.
- Relocation, scrub, and NOCOW write paths.

## Concurrency Notes

The comments document which fields are protected by which locks. `lock`, `free_space_lock`, `groups_sem`, `block_group_cache_lock`, and list-specific locks in `fs_info` are all part of the contract.

`frozen`, `reservations`, and `nocow_writers` are atomic counters used to safely coordinate removal/trim/scrub and allocation/write races.

List fields are intentionally overloaded across multiple owners, so callers must use the correct lock and helper API.

## Risks And Edge Cases

`btrfs_block_group_available_space()` assumes the block-group lock is held; callers that do not honor this can race accounting updates.

`bg_list` is shared among unused, reclaim, deleted, and new block-group lists, so incorrect list movement can corrupt lifecycle state.

`ro` is a counter, not a boolean. Read-only entry/exit must balance.

Zoned fields are meaningful only under zoned mode, but the struct stores them unconditionally.

## Testing Signals

This header's contracts are validated indirectly through:
- Allocation/free accounting tests.
- Block-group lookup and removal tests.
- Reclaim and relocation tests.
- Async discard tests.
- Zoned filesystem tests.
- Swapfile-on-Btrfs tests.
- Free-space cache/tree mount and transaction commit tests.
