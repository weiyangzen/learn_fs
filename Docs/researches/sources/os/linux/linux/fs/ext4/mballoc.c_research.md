# File Research: sources/os/linux/linux/fs/ext4/mballoc.c

## Purpose

Implements ext4's multiblock allocator: block/cluster allocation, preallocation, buddy cache management, delayed freeing, discard/TRIM, allocator statistics, and KUnit-visible test hooks. It is the main allocator behind `ext4_mb_new_blocks()` and `ext4_free_blocks()`.

## Major Responsibilities

- Builds and maintains per-block-group in-memory buddy bitmaps from on-disk block bitmaps plus active preallocation descriptors.
- Supports inode preallocation for larger/streaming files and locality-group preallocation for small file clustering.
- Searches for free space using multiple criteria:
  - `CR_POWER2_ALIGNED`
  - `CR_GOAL_LEN_FAST`
  - `CR_BEST_AVAIL_LEN`
  - `CR_GOAL_LEN_SLOW`
  - `CR_ANY_FREE`
- Optionally accelerates group selection with xarrays keyed by largest free order and average fragment size when `MB_OPTIMIZE_SCAN` is enabled.
- Updates on-disk bitmaps, group descriptors, flex group counters, quota, and journal metadata.
- Defers reuse of journaled freed metadata/data blocks until commit via `ext4_free_data`.
- Issues discard/TRIM for freed or explicitly trimmed extents.

## Key Data and Caches

- `ext4_pspace_cachep`: slab cache for `struct ext4_prealloc_space`.
- `ext4_ac_cachep`: slab cache for `struct ext4_allocation_context`.
- `ext4_free_data_cachep`: slab cache for delayed free records.
- `ext4_groupinfo_caches[]`: block-size-specific slab caches for `struct ext4_group_info`.
- `s_buddy_cache`: synthetic inode storing buddy-cache folios, two logical blocks per block group: bitmap then buddy.
- `s_mb_largest_free_orders[]`: xarrays of groups by largest free buddy order.
- `s_mb_avg_fragment_size[]`: xarrays of groups by average free fragment order.
- Per-CPU `discard_pa_seq`: sequence signal used to decide whether allocation should retry after preallocation discard activity.

## Allocation Flow

`ext4_mb_new_blocks()` is the main entry point.

1. Handles fast commit replay with `ext4_mb_new_blocks_simple()`.
2. Claims free cluster reservations and quota unless delayed allocation already reserved space.
3. Allocates and initializes `ext4_allocation_context`.
4. Chooses inode vs group preallocation policy with `ext4_mb_group_or_file()`.
5. Attempts existing preallocation via `ext4_mb_use_preallocated()`.
6. If no PA is usable:
   - normalizes request with `ext4_mb_normalize_request()`;
   - allocates a PA descriptor;
   - searches buddy state with `ext4_mb_regular_allocator()`.
7. Marks selected clusters on disk with `ext4_mb_mark_diskspace_used()`.
8. Releases context, updates PA state, drops pinned buddy folios, unlocks locality group, and collects stats.

The allocator can retry after ENOSPC-like failure by discarding preallocations through `ext4_mb_discard_preallocations_should_retry()`.

## Buddy Cache and Group Scanning

`ext4_mb_load_buddy_gfp()` loads bitmap and buddy folios for a group, initializing them if needed through `ext4_mb_init_group()` and `ext4_mb_init_cache()`.

Buddy generation:
- Copies on-disk bitmap into the cache.
- Marks active preallocations as used via `ext4_mb_generate_from_pa()`.
- Builds higher-order buddy structures with `ext4_mb_generate_buddy()`.
- Maintains `bb_free`, `bb_fragments`, `bb_counters[]`, `bb_first_free`, largest free order, and average fragment order.

Scanning:
- `ext4_mb_find_by_goal()` first checks the goal extent.
- `ext4_mb_scan_groups()` chooses linear or optimized scan.
- `ext4_mb_scan_group()` filters groups, loads buddy state, locks the group, then scans.
- `ext4_mb_simple_scan_group()` handles power-of-two requests.
- `ext4_mb_complex_scan_group()` walks free extents in the bitmap.
- `ext4_mb_scan_aligned()` handles stripe-aligned allocation attempts.

## Preallocation Handling

Preallocation descriptors are represented by `struct ext4_prealloc_space`.

- Inode PAs are stored in an inode rbtree keyed by logical start.
- Group/locality PAs are stored in per-CPU locality group lists bucketed by free length order.
- `ext4_mb_new_inode_pa()` and `ext4_mb_new_group_pa()` create new descriptors after over-allocation.
- `ext4_mb_use_inode_pa()` and `ext4_mb_use_group_pa()` consume existing descriptors.
- `ext4_mb_put_pa()` removes and frees fully consumed descriptors.
- `ext4_discard_preallocations()` discards all inode PAs.
- `ext4_mb_discard_group_preallocations()` discards all reclaimable PAs in a block group.
- `ext4_mb_discard_lg_preallocations()` trims locality group lists when buckets grow too large.

The PA logic is highly lock-sensitive: inode PA trees use `i_prealloc_lock`, group PA lists use locality locks plus RCU, and group lists are synchronized with group locks to avoid buddy initialization races.

## Freeing and Deferred Reuse

`ext4_free_blocks()` validates and normalizes block ranges, handles buffer forgetting, cluster boundary expansion, and delegates to `ext4_mb_clear_bb()`.

`ext4_mb_clear_bb()`:
- Verifies block validity.
- Loads buddy state.
- Clears bits in the on-disk bitmap with `ext4_mb_mark_context()`.
- Either queues freed clusters in `bb_free_root`/`s_freed_data_list` until journal commit or immediately returns them to buddy state.
- Updates quota and free-cluster counters unless the caller requested special handling.

`ext4_process_freed_data()` runs after journal commit and calls `ext4_free_data_in_buddy()` to make delayed frees reusable. Optional discard work is queued afterward.

## TRIM and Range Query

- `ext4_trim_fs()` implements filesystem-wide FITRIM.
- `ext4_trim_all_free()` trims one group.
- `ext4_try_to_trim_range()` scans free extents and calls `ext4_trim_extent()`.
- `ext4_trim_extent()` temporarily marks the extent used in buddy state while issuing discard, preventing concurrent allocation.
- `ext4_mballoc_query_range()` iterates free extents in a group for metadata consumers.

## Initialization and Teardown

- `ext4_init_mballoc()` creates global slab caches.
- `ext4_mb_init()` initializes per-superblock allocator structures, xarrays, locality groups, tunables, buddy cache inode, and group info.
- `ext4_mb_release()` flushes discard work, frees group info, active PAs, buddy cache inode, xarrays, and locality groups.
- `ext4_exit_mballoc()` destroys caches after `rcu_barrier()`.

## Concurrency and Consistency

Critical synchronization:
- Block group lock protects group buddy/bitmap/group-info mutation.
- Inode `i_data_sem` serializes data block allocation paths.
- PA locks protect descriptor fields.
- Locality group mutex serializes group PA allocation.
- RCU protects group info and locality PA traversal.
- Buddy folio pinning prevents reinitialization while allocated bits have not yet reached disk.

The file includes extensive comments describing consistency between on-disk bitmap, in-core buddy, and PA descriptors.

## Error Handling and Corruption Defense

- Detects free-space count mismatches between bitmaps and group descriptors.
- Marks group block bitmaps corrupt with `EXT4_GROUP_INFO_BBITMAP_CORRUPT`.
- Validates allocation/freeing against filesystem metadata zones.
- Handles fast commit replay idempotently through simplified bitmap marking.
- Uses `AGGRESSIVE_CHECK` and `DOUBLE_CHECK` optional debug paths for buddy and bitmap consistency.
- Uses `WARN_ON`, `BUG_ON`, and `ext4_grp_locked_error()` in invariant-violation paths.

## Test Hooks

When `CONFIG_EXT4_KUNIT_TESTS` is enabled, wrappers export selected internal helpers, including bit operations, simple allocation, buddy generation/load/unload, diskspace marking, and free-block helpers.

## Research Notes

This file is central to ext4 correctness and performance. The most fragile areas are PA lifetime/race handling, buddy/on-disk bitmap synchronization, journal-delayed reuse, bigalloc cluster rounding, and optimized group xarray maintenance.
