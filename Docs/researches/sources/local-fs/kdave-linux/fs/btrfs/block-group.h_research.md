# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-group.h

This header defines the public block group model and API used by Btrfs allocation, free-space, discard, zoned, transaction, relocation, and cleanup code.

Primary declarations:
- `enum btrfs_disk_cache_state` tracks old free-space cache persistence: written, error, clear, setup.
- `enum btrfs_block_group_size_class` classifies data-only block groups into small, medium, large, or unset allocation classes.
- `enum btrfs_discard_state` tracks async discard phases, including fully remapped discard.
- `enum btrfs_chunk_alloc_enum` defines chunk allocation pressure modes from no-force to force-for-extent.
- `enum btrfs_block_group_flags` defines runtime-only flags such as removed, new, zone active, needs free-space tree insertion, fully remapped, and stripe removal pending.
- `enum btrfs_caching_type` tracks free-space cache state: no cache, started, finished, error.
- `struct btrfs_caching_control` is the refcounted async cache worker state.
- `struct btrfs_block_group` is the central in-memory representation of a logical block group.

Important `struct btrfs_block_group` fields:
- Addressing and ownership: `fs_info`, `start`, `length`, `flags`, `global_root_id`.
- Space counters: `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `zone_unusable`.
- Persistence mirrors: `last_used`, `last_remap_bytes`, `last_identity_remap_count`, `last_flags`.
- Free-space and cache state: `free_space_ctl`, `disk_cache_state`, `cached`, `caching_ctl`, bitmap thresholds.
- Placement in global structures: rb-tree node, raid-type list, cluster list, multipurpose `bg_list`, read-only list, discard list, dirty list, IO list, active zone list.
- Synchronization and lifetime: `lock`, `data_rwsem`, `free_space_lock`, `refs`, `frozen`, `reservations`, `nocow_writers`.
- Zoned state: `alloc_offset`, `zone_capacity`, `meta_write_pointer`, `physical_map`, `last_eb`.
- Allocation policy: `full_stripe_len`, `size_class`, `reclaim_mark`.

Inline helpers:
- `btrfs_block_group_end()` returns exclusive logical end.
- `btrfs_is_block_group_used()` checks used, reserved, pinned, or remap bytes under the block group lock.
- `btrfs_is_block_group_data_only()` excludes mixed data/metadata groups from data-only optimizations.
- `btrfs_block_group_available_space()` subtracts used, pinned, reserved, super, and zoned-unusable bytes.
- `btrfs_block_group_done()` uses a memory barrier before checking finished/error cache states.
- Allocation profile helpers wrap `btrfs_get_alloc_profile()` for data, metadata, and system groups.

API surface:
- Lookup and iteration: `btrfs_lookup_first_block_group()`, `btrfs_lookup_block_group()`, `btrfs_next_block_group()`.
- Lifetime: `btrfs_get_block_group()`, `btrfs_put_block_group()`.
- Cache and free-space loading: `btrfs_cache_block_group()`, `btrfs_add_new_free_space()`.
- Read-only, NOCOW, reservation, swap, freeze, and size-class controls.
- Mount/read, create, remove, dirty-writeback, chunk allocation, reclaim, and teardown entry points.

The header is the contract that lets allocator, transaction, discard, zoned, inode/free-space-cache, relocation, and volume/chunk code coordinate around the same block group object.
