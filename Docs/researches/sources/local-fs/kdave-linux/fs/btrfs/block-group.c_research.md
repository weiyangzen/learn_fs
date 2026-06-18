# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-group.c

This file is the main Btrfs block group implementation. It manages block group creation, lookup, reference lifetime, free-space discovery, read-only transitions, removal, reclaim, chunk allocation, dirty block group persistence, and teardown.

Major responsibilities:
- Maintains the filesystem-wide block group cache as an rb-tree keyed by logical start.
- Selects allocation profiles with balance/restripe awareness via `btrfs_get_alloc_profile()`.
- Implements refcounted block group lifetime with `btrfs_get_block_group()` and `btrfs_put_block_group()`.
- Coordinates NOCOW writers, pending reservations, trim/scrub freezing, swap extents, and read-only block group transitions.
- Loads and maintains free-space state from the old space cache, free-space tree, or extent tree scan.
- Creates, persists, updates, and removes block group items and related device extent records.
- Drives unused block group deletion and reclaim-by-relocation.
- Implements two-phase chunk allocation and system chunk metadata reservation.

Key data flows:
- Mount-time discovery starts in `btrfs_read_block_groups()`, finds block group items through `find_first_block_group()`, validates them against chunk maps with `read_bg_from_eb()`, builds in-memory `struct btrfs_block_group` objects in `read_one_block_group()`, excludes superblock stripes, loads zoned info, adds the group to the rb-tree and `space_info`, and initializes global block reserves.
- New chunk creation starts with `btrfs_chunk_alloc()`, which serializes allocation through `space_info->chunk_alloc` and `fs_info->chunk_mutex`, calls `do_chunk_alloc()`, creates a block group through lower volume code, inserts chunk metadata, and leaves extent-tree/device-tree insertion for phase 2.
- Phase 2 runs in `btrfs_create_pending_block_groups()`, inserting the block group item, chunk item if still needed, device extents, and free-space tree records before clearing the `BLOCK_GROUP_FLAG_NEW` runtime flag.
- Allocation accounting uses `btrfs_add_reserved_bytes()` to move bytes from may-use to block group reserved state, `btrfs_update_block_group()` to convert reserved bytes to used bytes or used bytes to pinned bytes, and `btrfs_free_reserved_bytes()` to release unused reservations.

Free-space cache behavior:
- `btrfs_cache_block_group()` starts asynchronous caching unless the filesystem is zoned or the block group is remapped.
- `caching_thread()` samples size class, tries the old space cache when enabled, then uses the free-space tree or falls back to scanning extent items with `load_extent_tree_free()`.
- `btrfs_add_new_free_space()` adds ranges while skipping `fs_info->excluded_extents`, which are populated by `exclude_super_stripes()`.
- Caching has progress wakeups through `struct btrfs_caching_control`, `CACHING_CTL_WAKE_UP`, and `btrfs_wait_block_group_cache_progress()`.

Removal and reclaim:
- `btrfs_remove_block_group()` requires the group to be read-only unless remapped, detaches it from allocation clusters, dirty/cache IO lists, rb-tree, `space_info`, sysfs, free-space cache/tree, and block group item storage.
- Removed groups can keep their chunk map until `frozen` users finish, protecting scrub/trim users from address reuse.
- `btrfs_delete_unused_bgs()` processes `fs_info->unused_bgs`, handles async discard, zoned reclaim heuristics, pinned extent cleanup, read-only marking, transaction removal, and deleted block group tracking.
- `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes and relocates sparse groups through `btrfs_reclaim_block_group()`.

Concurrency and locking:
- `fs_info->block_group_cache_lock` protects the rb-tree and caching block group list.
- `space_info->groups_sem` serializes allocator-facing list changes and read-only decisions.
- `space_info->lock` plus `block_group->lock` protect byte counters and state.
- `fs_info->unused_bgs_lock` protects `bg_list` membership across unused, reclaim, fully remapped, deleted, and new block group lists.
- `fs_info->chunk_mutex` serializes system chunk reservation and chunk tree modifications.
- `ro_block_group_mutex` prevents races with dirty block group cache writeback when toggling read-only state.
- Dirty block group lists are protected by `transaction->dirty_bgs_lock`; cache writeback is additionally coordinated by `cache_write_mutex`.

Important invariants:
- Block group items must match chunk maps by start, length, and type flags.
- Extents must not span block group boundaries in `btrfs_update_block_group()`.
- System chunk allocation must not recursively occur through `btrfs_chunk_alloc()`.
- A removed block group’s logical/physical range must not be reused while frozen trim/scrub users remain.
- Zoned filesystems bypass normal cache loading and depend on allocation offsets, zone capacity, active zones, and zone unusable accounting.
- Data-only non-zoned block groups may use size classes to reduce fragmentation.
