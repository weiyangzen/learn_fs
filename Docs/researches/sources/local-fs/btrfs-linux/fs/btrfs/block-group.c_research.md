# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-group.c

## Scope

This file implements Btrfs block-group lifecycle, allocation profile selection, free-space cache population, chunk creation/removal coordination, dirty block-group writeback during transaction commit, read-only transitions, unused/reclaim block-group cleanup, logical-to-physical reverse mapping for superblock exclusions, zoned block-group accounting hooks, swapfile block-group pins, and data block-group size-class tracking.

It is the operational implementation behind the declarations in `block-group.h` and depends heavily on space-info accounting, extent/tree roots, transactions, free-space cache/tree, chunk mapping, discard, relocation, scrub, zoned allocation, delayed refs, and sysfs.

## Main APIs And Entry Points

- `btrfs_get_alloc_profile()` combines requested DATA/METADATA/SYSTEM flags with currently available profile bits and balance conversion targets, then reduces them to a usable chunk profile.
- `btrfs_lookup_block_group()`, `btrfs_lookup_first_block_group()`, and `btrfs_next_block_group()` search the fs-wide cached rb-tree of block groups with reference handling.
- `btrfs_inc_nocow_writers()`, `btrfs_dec_nocow_writers()`, and `btrfs_wait_nocow_writers()` protect NOCOW writes from racing read-only transitions, relocation, scrub, and similar block-group state changes.
- `btrfs_cache_block_group()` starts or waits for free-space caching for a block group, except on zoned filesystems and remapped block groups where allocator behavior differs.
- `btrfs_add_new_free_space()` adds free regions to a block group's in-memory free-space cache while excluding superblock and other excluded extents.
- `btrfs_read_block_groups()` reads block-group items at mount, validates them against chunk mappings, initializes `space_info`, sysfs entries, free-space state, zoned state, and global reserves.
- `btrfs_make_block_group()` creates an in-memory block group for a newly allocated chunk and links it into the transaction's pending-new-block-groups list.
- `btrfs_create_pending_block_groups()` completes phase 2 of chunk allocation by inserting block-group items, chunk items when needed, device extent items, and free-space-tree entries.
- `btrfs_chunk_alloc()` is the public phase-1 chunk allocator for data/metadata block groups.
- `check_system_chunk()` and `btrfs_reserve_chunk_metadata()` reserve system metadata for chunk-tree modifications under `fs_info->chunk_mutex`.
- `btrfs_inc_block_group_ro()` and `btrfs_dec_block_group_ro()` transition block groups into and out of read-only state with space-info counter adjustments.
- `btrfs_update_block_group()` transfers bytes between used, reserved, pinned, readonly, and reclaimable accounting when extents are allocated or freed.
- `btrfs_add_reserved_bytes()` and `btrfs_free_reserved_bytes()` maintain reservation counters for allocator-selected block groups.
- `btrfs_start_dirty_block_groups()`, `btrfs_write_dirty_block_groups()`, and `btrfs_setup_space_cache()` prepare and commit dirty block-group item updates plus optional v1 free-space-cache writeback.
- `btrfs_delete_unused_bgs()`, `btrfs_reclaim_block_groups()`, `btrfs_mark_bg_unused()`, and `btrfs_mark_bg_to_reclaim()` drive automatic empty/low-used block-group cleanup.
- `btrfs_remove_block_group()` removes a block group and its persistent metadata as part of chunk removal.
- `btrfs_free_block_groups()` tears down all cached block groups and space-info objects during unmount.
- `btrfs_rmap_block()` maps a physical superblock location back to logical block-group offsets for exclusion.
- `btrfs_freeze_block_group()` and `btrfs_unfreeze_block_group()` delay chunk-map reuse while trim/scrub or similar users still hold deleted block-group references.
- `btrfs_inc_block_group_swap_extents()` and `btrfs_dec_block_group_swap_extents()` pin block groups used by active swapfiles.
- `btrfs_calc_block_group_size_class()`, `btrfs_use_block_group_size_class()`, and `btrfs_block_group_should_use_size_class()` implement data block-group size-class segregation.
- `btrfs_mark_bg_fully_remapped()` and `btrfs_populate_fully_remapped_bgs_list()` handle remapped block groups whose old chunk stripes/device extents still need cleanup.

## Control Flow And Behavior

Allocation profile selection first checks paused/running balance conversion state under `balance_lock`. If a conversion target applies, it returns that target profile. Otherwise it masks profiles by writable device count and selects the highest redundancy available in a fixed order: RAID1C4, RAID6, RAID1C3, RAID5, RAID10, RAID1, DUP, RAID0, then single/no profile.

Block groups live in `fs_info->block_group_cache_tree`, a cached rb-tree keyed by logical start. Lookup increments `refs`; removal erases the rb-node and drops the tree reference. `btrfs_next_block_group()` handles the case where the current group was removed while still referenced by falling back to a fresh lookup at the old end offset.

Free-space caching is asynchronous through `struct btrfs_caching_control`. `caching_thread()` locks the caching control and reads the commit root under `commit_root_sem`. It optionally samples extent items to infer data block-group size class, tries v1 space-cache loading when enabled, otherwise uses the free-space tree or scans the extent tree to discover gaps. Progress wakes allocation waiters after enough free space is found. It finalizes the block group as `BTRFS_CACHE_FINISHED` or `BTRFS_CACHE_ERROR`, clears excluded extents, wakes waiters, and drops the block-group/caching-control references.

Extent-tree free-space loading scans extent and metadata items from the commit root, adding gaps between used extents through `btrfs_add_new_free_space()`. It periodically drops and reacquires locks when rescheduling is needed or `commit_root_sem` is contended. Superblock mirror locations are excluded from free-space accounting through `exclude_super_stripes()` using `btrfs_rmap_block()`.

Mount-time block-group reading walks block-group items from either the block-group tree or extent tree depending on features. Each item is cross-checked against a chunk map for start, length, and type. `read_one_block_group()` creates the in-memory block group, loads used/remap counters, initializes zone info, excludes super stripes, pre-fills free space for empty non-zoned groups, marks full groups cached, links into the rb-tree and space-info lists, sets available allocation profile bits, and queues unused empty groups when appropriate. Rescue paths with missing roots or unsupported readonly features build dummy full block groups from chunk maps.

Chunk allocation is explicitly two phase. Phase 1, `btrfs_chunk_alloc()`, decides whether a data/metadata chunk is needed, serializes with `space_info->chunk_alloc` and `fs_info->chunk_mutex`, checks system chunk reservations, creates the chunk mapping and in-memory block group, and inserts the chunk item into the chunk tree. Phase 2, `btrfs_create_pending_block_groups()`, later inserts the block-group item in the block-group/extent tree and device extent items in the device tree. This separation avoids deadlocks when extent-tree COW triggers chunk allocation while holding btree locks.

System chunks are not allocated through `btrfs_chunk_alloc()`. Callers modifying the chunk tree reserve system space through `check_system_chunk()` or `btrfs_reserve_chunk_metadata()` while holding `chunk_mutex`. If existing system space is insufficient, `reserve_chunk_space()` may create a system chunk and attempt to insert its chunk item, but tolerates some failures because phase 2 can retry.

Block-group removal is a multi-stage transaction path. `btrfs_remove_block_group()` requires the group to be read-only unless it was remapped, clears excluded/special ranges, removes it from allocation clusters, treelog/data relocation tracking, dirty/cache IO lists, the rb-tree, space-info lists, sysfs, free-space cache/tree, and the persistent block-group item. It waits for caching when needed, cancels discard work, removes free-space inodes, adjusts space-info counters, marks the group removed, and only removes the chunk map immediately if no frozen users remain. Otherwise chunk-map removal is deferred until `btrfs_unfreeze_block_group()`.

Unused block-group deletion and reclaim are separate cleaner flows. `btrfs_delete_unused_bgs()` handles empty or effectively empty groups, respecting async discard, zoned unusable space, mixed space-info, active reservations, read-only state, singleton profile groups, pinned extents, and unwritten zoned metadata. `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes and relocates low-used groups under an exclusive balance operation, periodically prioritizing unused-group cleanup.

Dirty block groups are transaction-scoped. `btrfs_update_block_group()` changes superblock bytes-used, block-group `used/reserved/pinned`, space-info `bytes_used/bytes_reserved/bytes_pinned`, reclaimable accounting, and dirty-list membership. Dirty list insertion is paired with delayed-ref reservation accounting. Commit paths first try to write easy free-space caches before the commit critical section, then retry and finish dirty block groups inside the critical section.

The v1 free-space cache path uses a hidden free-space inode per block group. `cache_save_setup()` creates or looks up that inode, sets its generation to 0 before writing so failures invalidate the cache, truncates stale cache contents, preallocates cache file space, and transitions `disk_cache_state`. `btrfs_write_dirty_block_groups()` waits for outstanding cache IO and updates block-group items before commit completes.

Read-only transitions check swapfile users, account available bytes into `space_info->bytes_readonly`, and on zoned filesystems migrate `zone_unusable` into readonly accounting. The public `btrfs_inc_block_group_ro()` coordinates with transactions and dirty-block-group writeback, optionally preallocates replacement chunks, avoids system chunk storms, and uses `ro_block_group_mutex`.

Size classes apply only to non-zoned data-only block groups. During caching, the code samples up to five extent items to infer the smallest observed size class. During allocation, `btrfs_use_block_group_size_class()` sets an empty group's class or rejects mismatched allocations unless the allocator is in forced wrong-size-class mode.

Fully remapped block groups are tracked so dead chunk stripes/device extents are eventually removed. Async discard sets `BLOCK_GROUP_FLAG_STRIPE_REMOVAL_PENDING`; synchronous handling moves the group to `fully_remapped_bgs`. Mount-time population compares the block-group cache tree and mapping tree to find remapped groups whose identity remap count reached zero but whose chunk map still has stripes.

## State And Data Structures

- `struct btrfs_block_group` fields used here include `start`, `length`, `used`, `reserved`, `pinned`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `identity_remap_count`, `last_*` committed values, `flags`, `runtime_flags`, `ro`, `cached`, `disk_cache_state`, `caching_ctl`, `free_space_ctl`, `space_info`, rb/list nodes, `reservations`, `nocow_writers`, `swap_extents`, zoned offsets/capacity/write pointer, size class, and discard state.
- `fs_info` state touched includes block-group rb-tree and lock, mapping tree, space-info list, profile bits, balance control, chunk mutex, caching/unused/reclaim/fully-remapped lists, discard control, delalloc root lock, global roots, global block reserves, transaction list, zoned active groups, and feature flags.
- Transaction state includes `new_bgs`, `dirty_bgs`, `io_bgs`, `deleted_bgs`, delayed-ref reservation accounting, pinned extents, cache write mutex, writer wait queue, and transaction flags such as dirty-bg run and cache ENOSPC.
- Persistent items handled include block-group items, chunk items, device extent items, free-space tree entries, free-space cache inode items, superblock bytes-used, and feature/profile bits.
- Runtime flags include `BLOCK_GROUP_FLAG_NEW`, `REMOVED`, `CHUNK_ITEM_INSERTED`, `NEEDS_FREE_SPACE`, `FREE_SPACE_ADDED`, `FULLY_REMAPPED`, and `STRIPE_REMOVAL_PENDING`.

## Dependencies

- Space accounting: `space-info.c`, metadata reservation code, global and delayed-ref block reserves.
- Allocation and mapping: chunk creation/removal, chunk map rb-tree, device extents, RAID profile helpers, zoned allocation activation.
- Free-space mechanisms: v1 free-space cache inode, free-space tree, in-memory free-space cache and bitmap/extent conversion thresholds.
- Transactions: delayed refs, transaction commit phases, dirty block-group cache writeback, commit-root scanning.
- Relocation, balance, scrub, discard, swapfile activation, tree log cleanup, sysfs block-group type registration, rescue mount paths, and feature flags.

## Risks And Invariants

- Chunk allocation must preserve the phase-1/phase-2 split. Inserting block-group items too early can deadlock with extent-tree COW paths.
- `chunk_mutex` is central for system space reservation and chunk-tree modifications. System chunk allocation through the wrong path risks lock recursion and chunk-array exhaustion.
- Dirty block-group list membership owns delayed-ref reservation increments. Missing the paired decrement leaks reservation pressure; double decrement corrupts accounting.
- Block-group removal must remove free-space/tree metadata and persistent block-group items before marking removed, while retaining chunk maps if trim/scrub/frozen users may still need stable logical-to-physical mappings.
- Read-only transitions must wait for block-group reservations and NOCOW writers where required. Otherwise relocation, scrub, and direct NOCOW writes can race.
- Free-space cache loading scans commit roots without normal btree locking. It depends on `commit_root_sem`, skip-locking paths, and safe rescheduling points.
- Zoned filesystems have special invariants around `alloc_offset`, `zone_unusable`, `meta_write_pointer`, active zones, and the prohibition on superblock stripes inside sequential block groups.
- Swapfile extents prevent read-only transitions and block-group removal. `swap_extents` is protected by the block-group spinlock.
- Size-class assignment is best effort and intentionally approximate during cache loading, but allocation-time races must return `-EAGAIN` unless forced.
- Async discard can interpose on unused and fully-remapped block-group cleanup, so list placement and runtime flags must remain consistent across remount/commit boundaries.
