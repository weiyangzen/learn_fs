# File Research: sources/os/linux/linux-stable/fs/btrfs/block-group.c

## Purpose

`block-group.c` implements Btrfs block-group lifecycle and accounting. It covers allocation-profile selection, block-group lookup/refcounting, free-space caching, mount-time block-group loading, read-only transitions, unused block-group deletion, relocation-based reclaim, dirty block-group persistence, chunk allocation phases, system chunk metadata reservation, frozen block-group cleanup, swap extent pins, data block-group size classes, and fully remapped block-group recovery.

## Major Functional Areas

### Allocation Profile Selection

- `get_restripe_target()` checks active balance conversion state and returns a target profile for data, system, or metadata block groups.
- `btrfs_reduce_alloc_profile()` filters available profiles by writable device count and picks the highest redundancy profile available, preferring RAID1C4, RAID6, RAID1C3, RAID5, RAID10, RAID1, DUP, then RAID0.
- `btrfs_get_alloc_profile()` reads the filesystem's available profile bits under `profiles_lock`, combines them with the requested block-group type, and reduces to the chunk-format allocation profile.
- `set_avail_alloc_bits()` and `clear_avail_alloc_bits()` maintain `avail_data_alloc_bits`, `avail_metadata_alloc_bits`, and `avail_system_alloc_bits`.
- `clear_incompat_bg_bits()` clears RAID56 or RAID1C34 incompat bits only after verifying no remaining block groups use those profile families.

### Block-Group Cache And Lookup

- `btrfs_create_block_group()` allocates and initializes an in-memory `struct btrfs_block_group`, including free-space control, locks, lists, reference count, discard state, frozen counter, and size/full-stripe metadata.
- `btrfs_add_block_group_cache()` inserts the block group into `fs_info->block_group_cache_tree`, keyed by logical start.
- `btrfs_lookup_first_block_group()`, `btrfs_lookup_block_group()`, and `btrfs_next_block_group()` provide refcounted tree iteration and lookup.
- `btrfs_get_block_group()` / `btrfs_put_block_group()` manage lifetime. Final put warns about leaked pinned/reserved bytes, cancels any remaining discard list entry, frees free-space control, chunk physical maps, and the block-group object.

### NOCOW And Reservation Pins

- `btrfs_inc_nocow_writers()` looks up the containing block group, checks it is not read-only under `bg->lock`, increments `nocow_writers`, and returns a referenced block group.
- `btrfs_dec_nocow_writers()` decrements `nocow_writers`, wakes waiters at zero, and drops the lookup reference.
- `btrfs_wait_nocow_writers()` waits for all NOCOW writers to exit.
- `btrfs_dec_block_group_reservations()` and `btrfs_wait_block_group_reservations()` coordinate the window between extent allocation and ordered-extent creation, especially before relocating or removing read-only data block groups.

### Free-Space Caching

- `btrfs_get_caching_control()` and `btrfs_put_caching_control()` manage caching-control references.
- `btrfs_wait_block_group_cache_progress()` waits for free-space cache progress after allocation failure, requiring progress plus enough free space or cache completion.
- `load_extent_tree_free()` scans committed extent-tree items, derives gaps as free space, excludes superblock stripes, periodically wakes waiters, and reschedules to avoid starving commit-root users.
- `load_block_group_size_class()` samples up to five file extents from the committed extent tree to infer a best-effort data block-group size class.
- `caching_thread()` chooses old space cache, free-space tree, or extent-tree scan, updates `cached` state, optionally fragments free space under debug options, clears excluded extents, and wakes waiters.
- `btrfs_cache_block_group()` starts or joins caching work, except on zoned filesystems and remapped block groups where allocator behavior does not use the normal cache.
- `btrfs_add_new_free_space()` adds free ranges to the in-memory free-space cache while skipping `excluded_extents`.

### Mount-Time Loading

- `read_bg_from_eb()` verifies a block-group item matches the corresponding chunk map.
- `find_first_block_group()` scans the block-group root, which is either the block-group tree or extent tree depending on feature flags.
- `exclude_super_stripes()` maps physical superblock locations back to logical addresses and marks those logical stripes excluded from free space; zoned block groups must not contain superblock stripes.
- `read_one_block_group()` constructs an in-memory block group from an on-disk item, validates mixed/data/metadata compatibility, loads zoned information, initializes free-space state for full/empty/zoned cases, inserts it into caches and space info, marks empty groups unused or queues discard, and marks unwritable chunks read-only.
- `fill_dummy_bgs()` creates full dummy block groups from chunk maps for read-only rescue cases where block-group items cannot be trusted or loaded.
- `btrfs_read_block_groups()` scans all on-disk block-group items, handles old space-cache invalidation, adds sysfs profile entries, marks unmirrored RAID0/SINGLE groups read-only when mirrored groups exist, initializes global reserves, and verifies chunk/block-group mapping consistency. With `IGNOREBADROOTS`, it falls back to dummy block groups.

### Block-Group Removal And Unused Cleanup

- `remove_block_group_item()` deletes a block-group item from the block-group root.
- `btrfs_remove_bg_from_sinfo()` subtracts block-group totals from `space_info`.
- `btrfs_start_trans_remove_block_group()` calculates metadata reservation units needed to remove a block group and starts a transaction using the global reserve fallback.
- `btrfs_remove_block_group()` performs full removal:
  - Requires the block group to be read-only or remapped.
  - Cancels free-space cache I/O and dirty-list membership.
  - Removes free-space inode/cache state.
  - Erases the block group from the lookup tree and space-info RAID list.
  - Updates allocation profile availability and feature bits.
  - Waits for caching if needed and removes caching-control list entries.
  - Removes free-space tree entries and on-disk block-group item.
  - Marks the block group removed.
  - Removes the chunk map immediately only if no freezer is active.
- `clean_pinned_extents()` clears block-group ranges from current and previous transaction pinned extents under `unused_bg_unpin_mutex`.
- `btrfs_link_bg_list()` adds a block group to an fs list with consistent refcounting.
- `btrfs_delete_unused_bgs()` drains `unused_bgs`, skipping or retrying groups that are still used, read-only due to balance, singular for their profile, fully remapped, not fully discarded with async discard, needed for outstanding reservations, or still containing unwritten zoned metadata. Eligible groups are marked read-only, optionally zone-finished, have pinned extents cleared, and are removed through `btrfs_remove_chunk()`.

### Reclaim

- `should_reclaim_block_group()` triggers reclaim when a block group crosses below its reclaim threshold from above.
- `btrfs_reclaim_block_group()` validates that the group is not reserved, pinned, or read-only; skips empty groups into unused cleanup; sets it read-only; relocates its chunk; and records reclaim statistics/errors.
- `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes, runs relocation under the exclusive balance operation, interleaves unused block-group deletion to avoid long cleaner stalls, and preserves retry candidates.
- `btrfs_reclaim_bgs_work()`, `btrfs_reclaim_bgs()`, and `btrfs_mark_bg_to_reclaim()` connect reclaim to worker scheduling and threshold detection.
- Zoned filesystems use `btrfs_zoned_should_reclaim()` to decide whether reclaim should run.

### Read-Only State

- `inc_block_group_ro()` is the internal accounting path. It rejects swap-pinned groups, checks whether enough alternate space exists unless forced, increments `ro`, moves available or zone-unusable bytes into `bytes_readonly`, and links the group to `ro_bgs`.
- `btrfs_inc_block_group_ro()` wraps this with transaction handling, dirty-block-group commit synchronization, optional chunk preallocation, zoned activation, system chunk checks, read-only mount handling, and `ro_block_group_mutex`.
- `btrfs_dec_block_group_ro()` decrements `ro` and reverses readonly/zone-unusable accounting when the count reaches zero.
- `btrfs_inc_block_group_swap_extents()` refuses to pin swap extents in read-only groups, and `btrfs_dec_block_group_swap_extents()` releases swap pins.

### Dirty Block-Group Persistence

- `insert_block_group_item()` writes a new block-group item, including v2 remap fields when `REMAP_TREE` is enabled, and updates `last_*` mirrors.
- `update_block_group_item()` updates on-disk used/remap/identity-remap/flags values only when they changed, with rollback of `last_*` values on most failures.
- `cache_save_setup()` prepares old free-space cache writeback: creates/looks up free-space inodes, invalidates cache generation before writing, truncates stale cache files, preallocates contiguous cache space, and marks disk-cache state.
- `btrfs_setup_space_cache()` prepares dirty groups with `BTRFS_DC_CLEAR` before commit when old space cache is enabled.
- `btrfs_start_dirty_block_groups()` starts cache writeback before the transaction critical section, creates pending block groups, updates block-group items, retries once after delayed refs, and requeues groups whose item does not exist yet.
- `btrfs_write_dirty_block_groups()` completes dirty block-group updates in the commit critical section, waits for cache I/O, handles rare free-space endio races that create new block groups, and aborts the transaction on persistent metadata update errors.
- `btrfs_update_block_group()` updates superblock bytes-used, block-group `used/reserved/pinned`, space-info counters, pinned extents, dirty-list membership, unused-list membership, and reclaim-list membership.

### Chunk Allocation

- `should_alloc_chunk()` decides whether to allocate a chunk based on force mode, limited mode free-space threshold, and 80% usage.
- `btrfs_force_chunk_alloc()` forces allocation for a given type.
- `do_chunk_alloc()` reserves system chunk metadata, creates the chunk/block group, adds the chunk item, handles degraded/scrub/discard `-ENOSPC` exceptions by creating a system chunk and retrying, then returns a referenced block group.
- `btrfs_chunk_alloc()` is phase 1 of chunk allocation:
  - Rejects re-entry and direct system chunk allocation.
  - Serializes allocation through `space_info->chunk_alloc` and `fs_info->chunk_mutex`.
  - Preserves mixed data/metadata allocation behavior.
  - Optionally forces metadata allocation after a configured data/metadata ratio.
  - Creates the chunk and chunk item, activates zoned data groups for extent allocation, clears force/full state, and returns whether a chunk was allocated.
- `btrfs_create_pending_block_groups()` is phase 2:
  - Inserts block-group items.
  - Adds chunk items if not already inserted.
  - Inserts device extents.
  - Adds free-space tree entries.
  - Adds sysfs RAID profile entries.
  - Releases delayed-ref reservations for block-group inserts and marks still-unused new groups unused.
- The two-phase design prevents deadlocks from inserting extent-tree block-group items while COWing extent-tree nodes.

### System Chunk Metadata Reservation

- `get_profile_num_devs()` determines how many device items a profile can require.
- `reserve_chunk_space()` reserves system metadata in `chunk_block_rsv`, creating a system chunk if free system space is insufficient. It must run under `chunk_mutex`.
- `check_system_chunk()` reserves enough system space to add/remove a chunk item and update device items.
- `btrfs_reserve_chunk_metadata()` reserves system space for chunk-tree updates outside normal chunk allocation/removal.

### Teardown And Cleanup

- `btrfs_put_block_group_cache()` waits for caching and releases free-space inode references.
- `check_removing_space_info()` warns on leaked pinned/may-use/reserved/reclaim bytes and removes child subgroups.
- `btrfs_free_block_groups()` drains caching, unused, reclaim, fully-remapped, zoned-active, and rb-tree block-group lists; removes free-space caches; asserts list/refcount/swap invariants; releases global reserves; and removes space-info sysfs state. It must run after workers stop.
- `btrfs_freeze_block_group()` and `btrfs_unfreeze_block_group()` delay chunk-map removal while trim/scrub/discard users may still reference a removed block group. Final unfreeze removes the chunk map and any leftover free-space cache.

### Size Classes And Fully Remapped Groups

- `btrfs_calc_block_group_size_class()` maps allocation size to small (`<=128K`), medium (`<=8M`), or large.
- `btrfs_block_group_should_use_size_class()` enables size classes only for non-zoned data-only block groups.
- `btrfs_use_block_group_size_class()` sets or validates a block group's size class, returning `-EAGAIN` for racing first allocations of mismatched sizes unless forced.
- `btrfs_maybe_reset_size_class()` clears the class when an eligible group becomes empty and unreserved.
- `btrfs_mark_bg_fully_remapped()` queues remapped groups for async discard or the fully-remapped list.
- `btrfs_populate_fully_remapped_bgs_list()` reconstructs the fully-remapped list at mount by comparing block-group and chunk trees, handling cases where unmount happened before async discard removed dead stripes/device extents.

## Dependencies

- Btrfs subsystems: extent tree, block-group tree, free-space cache/tree, space-info accounting, chunk/device mapping, transactions, delayed refs, relocation, discard, sysfs, tree log, zoned allocation, RAID56 mapping, ref verification, and filesystem feature flags.
- Kernel primitives: rb trees, lists, refcounts, spinlocks, rwsems, mutexes, workqueues, wait queues, sequence locks, ratelimits, and kobjects.
- Important shared state:
  - `fs_info->block_group_cache_tree`
  - `fs_info->mapping_tree`
  - `fs_info->space_info`
  - `fs_info->unused_bgs`
  - `fs_info->reclaim_bgs`
  - `fs_info->fully_remapped_bgs`
  - `fs_info->caching_block_groups`
  - `fs_info->excluded_extents`
  - `space_info` counters and RAID lists
  - `transaction->dirty_bgs`, `io_bgs`, `deleted_bgs`, and `pinned_extents`

## Risks And Invariants

- Chunk allocation must preserve its two-phase structure. Inserting block-group items into the extent tree during phase 1 can deadlock with extent-tree COW.
- System chunk updates must be serialized by `chunk_mutex`; otherwise chunk-tree COW can recurse into system allocation.
- Block-group removal must keep chunk maps alive while `frozen` users exist, because trim/scrub/discard can still rely on old logical-to-physical mappings.
- Dirty block-group updates rely on delayed-ref reservation counters. Forgetting to increment/decrement update or insert reservations leaks metadata reserve state.
- Free-space cache writeback races with block-group deletion and free-space endio workers; `cache_write_mutex`, dirty locks, and `io_list` ownership are central.
- NOCOW writers, reservations, swap extents, and read-only transitions must be coordinated before relocation/removal to avoid writing into moved or read-only groups.
- Zoned mode changes accounting semantics: `alloc_offset`, `zone_unusable`, active groups, metadata write pointers, and zone finish/activation paths must stay consistent.
- Feature bits and available profile bits must only be cleared after verifying no remaining block groups use the profile.
- Size classes are an optimization; enforcement must allow desperate fallback without corrupting block-group accounting.
