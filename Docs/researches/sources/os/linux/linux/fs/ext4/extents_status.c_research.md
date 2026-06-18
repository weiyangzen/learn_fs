# File Research: sources/os/linux/linux/fs/ext4/extents_status.c

## Purpose

`extents_status.c` implements ext4's in-memory extent status tree. The tree caches logical ranges as written, unwritten, delayed, or hole extents, supports lookup and range scans for mapping, fiemap, SEEK_DATA/SEEK_HOLE, delayed allocation, and bigalloc accounting, and supplies shrinker integration for reclaimable cached extents. It also implements a pending cluster reservation tree used by bigalloc delayed-allocation accounting.

The file deliberately distinguishes authoritative mutation APIs from cache-only APIs:
- `ext4_es_insert_extent()` changes existing ES state after block mapping changes.
- `ext4_es_cache_extent()` only caches on-disk information when no conflicting state exists.
- `ext4_es_insert_delayed_extent()` adds delayed allocation state and pending reservations.

## Core Structures

- `ext4_es_cachep` allocates `struct extent_status` objects.
- `ext4_pending_cachep` allocates `struct pending_reservation` objects.
- Each inode has `EXT4_I(inode)->i_es_tree`, an RB tree ordered by `es_lblk`, and a single-entry `cache_es` hot lookup pointer.
- Each inode has `i_es_lock`, a rwlock protecting ES tree and pending reservation tree access.
- Superblock ES shrinker state includes `s_es_list`, `s_es_nr_inode`, `s_es_lock`, and `s_es_stats`.
- Reclaimable-object counts distinguish all ES entries (`i_es_all_nr`, `es_stats_all_cnt`) from shrinkable entries (`i_es_shk_nr`, `es_stats_shk_cnt`).
- Delayed extents are "must keep" because fiemap, bigalloc, and seek hole/data need them.

## Initialization

- `ext4_init_es()` creates the extent status slab cache.
- `ext4_exit_es()` destroys it.
- `ext4_es_init_tree()` initializes an inode ES RB root and clears the hot cache.
- `ext4_init_pending()` and `ext4_exit_pending()` manage the pending-reservation slab.
- `ext4_init_pending_tree()` initializes an inode pending-reservation RB root.
- `ext4_es_register_shrinker()` initializes ES counters/list state, allocates a named shrinker, and registers scan/count callbacks.
- `ext4_es_unregister_shrinker()` destroys counters and frees the shrinker.

## Lookup And Scan

- `ext4_es_end()` returns the inclusive logical end of an ES entry and asserts no wrap.
- `ext4_es_inc_seq()` increments `i_es_seq` to let callers detect ES mutations.
- `__es_tree_search()` finds an extent containing `lblk`, or the next extent after `lblk`.
- `__es_find_extent_range()` returns the first extent matching a caller-supplied predicate in or after a logical range, using the hot cache first.
- `ext4_es_find_extent_range()` wraps range search with read locking and disables normal behavior during fast-commit replay.
- `__es_scan_range()` reports whether any matching extent intersects a range.
- `ext4_es_scan_range()` and `ext4_es_scan_clu()` provide locked external scan helpers; cluster scan maps `lblk` to the containing bigalloc cluster.
- `ext4_es_lookup_extent()` is the main map-blocks lookup. It searches the hot cache then RB tree, copies the found entry, marks it referenced for reclaim aging, updates cache hit/miss counters, optionally returns the next logical extent start, and optionally returns the ES sequence.

## Allocation, Freeing, And Merge

- `__es_alloc_extent()` allocates an ES entry, optionally nofail.
- `ext4_es_init_extent()` initializes an ES entry and updates inode/superblock object counters. Non-must-keep entries add the inode to the shrinker list when needed.
- `ext4_es_free_extent()` decrements counters, removes the inode from the shrinker list when no shrinkable entries remain, and frees the entry.
- `ext4_es_must_keep()` currently keeps delayed extents from reclaim.
- `ext4_es_can_be_merged()` allows merge when type matches, logical ranges are adjacent, length does not exceed `EXT_MAX_BLOCKS`, and physical ranges are adjacent for written/unwritten types. Holes and delayed extents merge by logical adjacency.
- `ext4_es_try_to_merge_left()` and `ext4_es_try_to_merge_right()` merge adjacent RB neighbors and preserve the referenced bit if either merged entry had it.
- `__es_insert_extent()` inserts a non-overlapping ES entry or merges with adjacent entries. It assumes overlaps were removed first and updates `cache_es`.

## Insert And Cache APIs

- `ext4_es_insert_extent()` is used when block mappings are modified. It:
  - Ignores operations during fast-commit replay.
  - Rejects zero-length inserts.
  - Warns if callers try to insert delayed status through this API.
  - Removes any existing ES entries in the range.
  - Inserts the new written/unwritten/hole entry.
  - For bigalloc delayed allocation, revises pending reservations after written/unwritten mappings replace delayed ranges.
  - Updates reserved cluster accounting through `ext4_da_update_reserve_space()`.
  - Retries with nofail preallocations when allocation failures occur.
- `ext4_es_cache_extent()` is cache-only. It checks existing entries for status conflicts, removes same-status overlaps, inserts the cached extent, and warns on real conflicts. A hole conflicting with a delayed extent is explicitly allowed.
- With `ES_AGGRESSIVE_TEST__`, `ext4_es_insert_extent_check()` verifies inserted ES entries against either the on-disk extent tree or indirect block mapping, catching mismatches during debug/test builds.

## Removal And Reservation Accounting

- `__es_remove_extent()` removes a logical range from the ES tree. It can:
  - Check that removed entries match a requested status mask.
  - Split one ES entry into left/right remnants.
  - Remove whole entries across the middle of a range.
  - Adjust physical block starts for right remnants of written/unwritten extents.
  - Count released delayed reservations when `reserved` is provided and delalloc is active.
  - Cancel pending reservations as appropriate.
- `ext4_es_remove_extent()` wraps removal with write locking, unconditional locking for inode reclaim synchronization, nofail retry allocation for splits, sequence increment, trace emission, and `ext4_da_release_space()` for released delayed reservations.
- `init_rsvd()`, `count_rsvd()`, and `get_rsvd()` cooperate to count delayed blocks/clusters removed from ES:
  - Non-bigalloc simply counts delayed blocks.
  - Bigalloc counts full and partial clusters without double-counting across adjacent extents.
  - Clusters still delayed at removed-range edges remain reserved.
  - Pending reservations inside the removed cluster range reduce the released count and are removed.

## Shrinker

- `ext4_es_list_add()` and `ext4_es_list_del()` track inodes with shrinkable ES entries on a per-superblock list.
- `__es_shrink()` walks the inode list, skipping precached inodes on the first pass, avoiding the currently locked inode, using `write_trylock()` for inode ES locks, and falling back to a locked inode if supplied. It records scan time and shrink averages.
- `ext4_es_count()` reports shrinkable ES object count.
- `ext4_es_scan()` invokes `__es_shrink()` and traces before/after counts.
- `ext4_seq_es_shrinker_info_show()` prints object counts, cache hit/miss counts, inode list size, average scan time, average shrink count, max-object inode, and max scan time.
- `es_do_reclaim_extents()` scans from `i_es_shrink_lblk` to an end point, clears referenced bits on first encounter, frees unreferenced shrinkable entries, and updates the next scan cursor.
- `es_reclaim_extents()` wraps scan-around behavior and warns if forced to shrink precached extents.
- `ext4_clear_inode_es()` implements `EXT4_IOC_CLEAR_ES_CACHE` semantics: it removes only discretionary entries, keeps must-keep delayed entries, clears the hot cache, and clears `EXT4_STATE_EXT_PRECACHED`.

## Pending Cluster Reservations

Pending reservations track bigalloc clusters that contain delayed/unwritten blocks plus allocated written/unwritten blocks such that quota/reservation accounting must be corrected if one side disappears.

- `__get_pending()` looks up a logical cluster in the pending RB tree.
- `__pr_tree_search()` finds a pending reservation by cluster or the next cluster after it.
- `__insert_pending()` inserts a cluster reservation if absent, using an optional preallocated entry and returning whether a new reservation was inserted.
- `__remove_pending()` removes a pending reservation if present.
- `ext4_remove_pending()` and `ext4_is_pending()` provide locked external removal/query helpers.
- `ext4_es_insert_delayed_extent()` inserts delayed ES state and optionally inserts pending reservations for the first and/or end clusters if physical clusters are already allocated. It retries with nofail allocations on memory pressure and increments `i_es_seq` after success.
- `__revise_pending()` is called after written/unwritten extents replace delayed ranges. It examines delayed blocks outside the newly allocated range within the first and last clusters to decide whether to insert, retain, or remove pending reservations. It returns the number of newly inserted pending reservations or a negative error.

## Fast-Commit Replay Behavior

Most public ES operations return immediately or report misses while `EXT4_FC_REPLAY` is set:
- `ext4_es_find_extent_range()` returns empty.
- `ext4_es_scan_range()` and `ext4_es_scan_clu()` return false.
- `ext4_es_insert_extent()`, `ext4_es_cache_extent()`, `ext4_es_lookup_extent()`, `ext4_es_remove_extent()`, and `ext4_es_insert_delayed_extent()` avoid normal ES mutation/lookup during replay.

This prevents replay from trusting or mutating in-memory state that is being reconstructed from log/on-disk data.

## Locking And Consistency Rules

- `i_es_lock` protects both ES tree and pending reservation tree.
- Public lookup/scan helpers use read locks; insert/remove/reclaim/clear paths use write locks.
- The large file-level comments define a stricter consistency contract:
  - Normal block mapping creation/query should go through ES instead of hand-managed on-disk tree state.
  - On-disk extent tree updates require exclusive `i_data_sem` and atomic ES updates.
  - If `i_data_sem` may be dropped for a large operation, callers must hold `i_rwsem` and `invalidate_lock`, evict affected page cache, and rebuild/drop ES as needed.
  - Mapping queries must hold `i_rwsem`, `invalidate_lock`, or relevant folio locks for the range.
- The shrinker relies on `i_es_lock` to avoid racing inode reclaim.

## Failure And Risk Areas

- ES entry insertion/removal can require splitting existing entries; public wrappers use retry loops and nofail preallocation to avoid losing must-keep delayed state under memory pressure.
- `ext4_es_cache_extent()` intentionally does not convert conflicting state; misuse for authoritative updates would leave stale mappings.
- Pending reservation accounting is subtle around first/last partial clusters, especially when a range starts and ends in the same cluster.
- Shrinker reclamation skips delayed extents but may reclaim written/unwritten/hole cache entries; callers must tolerate cache misses and reload from the extent tree.
- The hot `cache_es` pointer is invalidated on removals and clear/reclaim paths; stale use would be unsafe without `i_es_lock`.
