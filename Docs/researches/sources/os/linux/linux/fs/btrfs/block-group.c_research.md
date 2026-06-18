# File Research: sources/os/linux/linux/fs/btrfs/block-group.c

## Scope And Role

`block-group.c` implements Btrfs block-group lifecycle and allocation accounting. A block group is the logical chunk-level allocation unit that connects free-space state, space-info counters, chunk/device mappings, block-group items in trees, relocation/reclaim, discard, read-only transitions, zoned allocation state, and transaction commit writeback.

The file covers:

- Allocation profile selection.
- Block-group lookup and reference management.
- Free-space cache loading and block-group caching workers.
- Mount-time block-group reconstruction.
- Block-group creation and deletion.
- Dirty block-group commit/update paths.
- Chunk allocation phase orchestration.
- Reservation and used/pinned accounting.
- Reclaim and unused block-group cleanup.
- Read-only/frozen/swap-safe block-group transitions.
- Size-class optimization for data block groups.
- Fully remapped block-group handling.

## Major Data Flow

### Mount/read path

`btrfs_read_block_groups()` selects the block-group root, scans block-group items, reads each item with `read_one_block_group()`, creates in-memory `struct btrfs_block_group` objects, initializes zone/free-space state, adds them to the rb tree and `space_info`, sets available allocation bits, and initializes global reserves.

If normal block-group items cannot be read under rescue/unsupported read-only conditions, `fill_dummy_bgs()` creates full dummy block groups from the chunk mapping tree so the filesystem can still mount for recovery.

`check_chunk_block_group_mappings()` validates that every chunk map has a matching block group with identical start, length, and type flags.

### Cache loading path

`btrfs_cache_block_group()` starts a `btrfs_caching_control` worker unless the group is already cached, zoned mode bypasses caching, or a remapped group cannot allocate.

`caching_thread()` loads size-class hints, tries the old space cache if enabled, then loads free ranges from either the free-space tree or extent tree. It updates `cache->cached`, wakes waiters, frees excluded super extents, and drops references.

`load_extent_tree_free()` scans committed extent-tree items and adds gaps as free space while periodically waking allocation waiters after `CACHING_CTL_WAKE_UP`.

`btrfs_wait_block_group_cache_progress()` and `btrfs_wait_block_group_cache_done()` let allocators wait for usable progress or completion.

### Creation path

`btrfs_make_block_group()` creates a new in-memory block group for a newly allocated chunk, marks it `BLOCK_GROUP_FLAG_NEW`, initializes free space, inserts it in the rb tree and `space_info`, updates global reserves, adds it to the transaction's pending `new_bgs` list, increments delayed-ref reservation accounting, and sets available profile bits.

`btrfs_create_pending_block_groups()` is phase 2 of chunk allocation. It inserts the block-group item, chunk item if still missing, device extent items, and free-space tree records, then clears the new flag and marks unused groups for possible cleanup.

### Deletion path

`btrfs_delete_unused_bgs()` processes `fs_info->unused_bgs`, skips unsafe candidates, coordinates async discard and zoned zone finishing, marks empty groups read-only, starts a removal transaction, clears pinned extents, removes the chunk, and moves groups to transaction deleted lists when trimming must complete at commit.

`btrfs_remove_block_group()` removes a block group from all runtime structures and on-disk metadata: free-space inode/cache, rb tree, space-info lists, free-space tree, block-group item, and possibly chunk map. It carefully handles caching controls, dirty/io lists, sysfs entries, discard, frozen users, and remapped groups.

`btrfs_start_trans_remove_block_group()` calculates metadata units needed to remove a block group and starts a fallback-global-reserve transaction.

### Reclaim path

`btrfs_mark_bg_to_reclaim()` links groups into `fs_info->reclaim_bgs`.

`btrfs_reclaim_block_groups()` sorts candidates by used bytes, uses an exclusive balance operation, and relocates underused groups through `btrfs_reclaim_block_group()` until a limit is reached.

`btrfs_reclaim_block_group()` validates the group still qualifies, marks it read-only, records used/reserved bytes, relocates the chunk, updates reclaim stats, and requeues on recoverable failure.

`btrfs_reclaim_bgs()` performs periodic reclaim sweep and schedules worker execution.

### Dirty/update/commit path

`btrfs_update_block_group()` adjusts super bytes-used, block-group `used/reserved/pinned`, `space_info` counters, dirty-list membership, pinned extents, reclaim eligibility, and unused-group detection when extents are allocated or freed.

`btrfs_start_dirty_block_groups()` begins space-cache writeout and block-group item updates before the transaction critical section to reduce commit latency.

`btrfs_write_dirty_block_groups()` finishes dirty block-group updates in the commit critical section, waits for cache I/O, runs delayed refs, retries rare missing-item races, and drains `io_bgs`.

`update_block_group_item()` persists used/remap/identity-remap/flags changes back to the block-group item and rolls back last-committed snapshots on failure.

`cache_save_setup()` prepares old space-cache inode writeout, including inode lookup/creation, generation invalidation, truncation, preallocation, and cache disk state transitions.

### Chunk allocation path

`btrfs_chunk_alloc()` is phase 1 for data/metadata chunks. It decides whether allocation is needed, serializes through `space_info->chunk_alloc` and `fs_info->chunk_mutex`, rejects system chunk allocation through this path, handles mixed block groups and metadata-ratio forcing, creates the chunk, and records success/failure in `space_info`.

`do_chunk_alloc()` checks system chunk space, creates the chunk, inserts the chunk item, handles rare `-ENOSPC` by creating an extra system chunk and retrying, and releases chunk metadata reservations.

`check_system_chunk()` and `btrfs_reserve_chunk_metadata()` reserve system space for chunk-tree updates under `chunk_mutex`.

The long comment above `btrfs_chunk_alloc()` documents why chunk allocation is split into two phases: inserting extent-tree block-group items during allocation can deadlock with COW of locked extent-tree nodes.

## Key Functions

Allocation profile:
- `get_restripe_target()`
- `btrfs_reduce_alloc_profile()`
- `btrfs_get_alloc_profile()`
- `set_avail_alloc_bits()`
- `clear_avail_alloc_bits()`
- `clear_incompat_bg_bits()`

Lookup/refcount:
- `btrfs_get_block_group()`
- `btrfs_put_block_group()`
- `btrfs_lookup_first_block_group()`
- `btrfs_lookup_block_group()`
- `btrfs_next_block_group()`

NOCOW/reservation synchronization:
- `btrfs_inc_nocow_writers()`
- `btrfs_dec_nocow_writers()`
- `btrfs_wait_nocow_writers()`
- `btrfs_dec_block_group_reservations()`
- `btrfs_wait_block_group_reservations()`

Free-space/cache:
- `btrfs_add_new_free_space()`
- `load_extent_tree_free()`
- `btrfs_cache_block_group()`
- `btrfs_wait_block_group_cache_progress()`
- `btrfs_wait_block_group_cache_done()`

Read/create/remove:
- `btrfs_read_block_groups()`
- `btrfs_make_block_group()`
- `btrfs_create_pending_block_groups()`
- `btrfs_remove_block_group()`
- `btrfs_delete_unused_bgs()`

Accounting:
- `btrfs_update_block_group()`
- `btrfs_add_reserved_bytes()`
- `btrfs_free_reserved_bytes()`

Chunk metadata:
- `btrfs_chunk_alloc()`
- `btrfs_force_chunk_alloc()`
- `check_system_chunk()`
- `btrfs_reserve_chunk_metadata()`

Teardown and special states:
- `btrfs_put_block_group_cache()`
- `btrfs_free_block_groups()`
- `btrfs_freeze_block_group()`
- `btrfs_unfreeze_block_group()`
- `btrfs_inc_block_group_swap_extents()`
- `btrfs_dec_block_group_swap_extents()`

Size/remap:
- `btrfs_calc_block_group_size_class()`
- `btrfs_use_block_group_size_class()`
- `btrfs_block_group_should_use_size_class()`
- `btrfs_mark_bg_fully_remapped()`
- `btrfs_populate_fully_remapped_bgs_list()`

## Important State And Locking

`fs_info->block_group_cache_lock` protects the rb tree of block groups.

`space_info->groups_sem` protects block-group lists per raid/profile type and blocks allocator races during removal/reclaim/read-only transitions.

`space_info->lock` and `block_group->lock` protect accounting fields such as `used`, `reserved`, `pinned`, `ro`, `zone_unusable`, and `swap_extents`.

`fs_info->unused_bgs_lock` protects `unused_bgs`, `reclaim_bgs`, and `fully_remapped_bgs` list membership through `bg_list`.

`fs_info->chunk_mutex` serializes chunk-tree updates, system chunk reservation, and chunk allocation/removal.

`trans->transaction->dirty_bgs_lock` protects transaction dirty/io block-group lists.

`ro_block_group_mutex` prevents setting groups read-only after dirty block-group commit processing has begun.

`caching_control->mutex`, waitqueue, refcount, and `progress` coordinate async cache loading with allocators.

## On-Disk Integration

The file reads and writes:

- `BTRFS_BLOCK_GROUP_ITEM_KEY` in either the block-group tree or extent tree depending on `BLOCK_GROUP_TREE`.
- Chunk tree records via `btrfs_chunk_alloc_add_chunk_item()`.
- Device extent items in the device tree.
- Free-space tree records.
- Old free-space cache inodes.
- Superblock `bytes_used`.

It also cross-checks chunk map records against block-group items during mount.

## Zoned Filesystem Handling

Several paths branch on `btrfs_is_zoned()`:

- Free-space cache loading is skipped for zoned allocation.
- `has_unwritten_metadata()` checks `meta_write_pointer`.
- `read_one_block_group()` calls `btrfs_calc_zone_unusable()`.
- Read-only transitions migrate `zone_unusable` into/out of `bytes_readonly`.
- New chunks may be activated for zoned allocation.
- Empty zoned groups may be finished before removal.
- Superblock stripes are forbidden inside sequential zones.
- Size classes are disabled for zoned filesystems.

## Reflink/Remap Handling

For the remap tree feature, block-group item v2 includes `remap_bytes` and `identity_remap_count`.

Fully remapped groups are tracked by `BLOCK_GROUP_FLAG_FULLY_REMAPPED`, `BLOCK_GROUP_FLAG_STRIPE_REMOVAL_PENDING`, and `fs_info->fully_remapped_bgs`. `btrfs_populate_fully_remapped_bgs_list()` reconstructs pending fully-remapped groups after mount by comparing block-group and chunk trees.

## Error Handling And Corruption Checks

The file uses `-EUCLEAN` for structural inconsistencies such as missing block-group roots, chunk/block-group mismatches, or invalid zoned superblock placement.

Transaction-impacting failures usually call `btrfs_abort_transaction()`.

Several paths tolerate `-ENOSPC` intentionally:
- Marking block groups read-only may allocate fallback chunks.
- System chunk reservation may pre-create chunks but ignore some failures until needed.
- Space-cache setup may skip cache writeout on ENOSPC.

Warnings protect invariants around refcounted teardown, dirty/io list state, pinned/reserved accounting, swap extents, and chunk-map removal timing.

## Risks And Edge Cases

The most fragile behavior is concurrency around block-group removal. Removal must coordinate allocators, scrub, trim/discard, free-space cache I/O, frozen block groups, and transaction commit. Removing the chunk map too early can allow logical/physical ranges to be reused while trim or scrub still references them.

The two-phase chunk allocation protocol is mandatory. Collapsing it into a single insertion path can deadlock with extent-tree or chunk-tree COW.

`btrfs_update_block_group()` must load old free-space cache before freeing space if cache state is not complete, otherwise unpinning can leak space.

`space_info->full` can be set after `-ENOSPC`; later code must clear/reset allocation pressure through existing mechanisms rather than assuming permanent media exhaustion.

Size-class enforcement can return `-EAGAIN` on races for newly empty block groups. Allocator callers must retry or relax with `force_wrong_size_class`.

## Testing Signals

Important coverage areas:

- Mount with valid, missing, mismatched, and rescue block-group/chunk records.
- Empty block-group deletion with and without async discard.
- Dirty block-group update during transaction commit and pre-commit.
- Chunk allocation under degraded profiles, scrub-induced read-only groups, and discard races.
- Zoned block-group activation, finish, read-only transitions, and unwritten metadata checks.
- Reclaim threshold crossing and relocation failure requeue.
- Old space-cache setup/truncate/writeout and free-space tree mode.
- Fully remapped block groups across unmount/remount.
- Swapfile extents preventing read-only transitions.
