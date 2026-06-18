# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.c

Implements XFS refcount btree semantic operations for reflink/shared blocks and CoW staging records. It covers lookup, record validation, insertion/deletion/update, range refcount increase/decrease, CoW reservation tracking, crash recovery of leftover CoW reservations, and deferred refcount intent execution for both AG and realtime group refcount btrees.

Key responsibilities:
- Converts on-disk refcount records to in-core `xfs_refcount_irec`, including shared vs CoW domain decoding via `XFS_REFC_COWFLAG`.
- Validates refcount records against AG or rtgroup geometry, domain rules, length limits, and refcount limits.
- Performs normalized range updates by splitting records at adjustment boundaries, merging adjacent compatible records, then adjusting middle records.
- Treats holes in the shared refcount btree as implicit refcount-1 allocated extents during file extent updates.
- Deletes records when shared refcount drops to 1, schedules block frees when refcount drops to 0, and pins saturated `XFS_REFC_REFCOUNT_MAX` records.
- Tracks CoW staging extents as domain-COW records with refcount 1, distinct from shared records.
- Recovers orphaned CoW staging allocations after crashes by scanning domain-COW records, freeing their rmap entries and blocks.
- Implements deferred operation finishers: `xfs_refcount_finish_one` for AGs and `xfs_rtrefcount_finish_one` for rtgroups.

Important functions:
- `xfs_refcount_lookup_le/ge/eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`
- `xfs_refcount_split_extent`, `xfs_refcount_merge_extents`, `xfs_refcount_adjust_extents`, `xfs_refcount_adjust`
- `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`
- `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`
- `xfs_refcount_find_shared`
- `xfs_refcount_recover_cow_leftovers`
- `xfs_refcount_has_records`, `xfs_refcount_query_range`
- `xfs_refcount_intent_init_cache`, `xfs_refcount_intent_destroy_cache`

Design notes:
- The file is transaction-reservation aware; `xfs_refcount_still_have_space` limits per-transaction dirtying and supports continuation intents.
- AG and realtime paths share the same core adjust logic because both expose group-relative btree cursors.
- Refcount shape changes are tracked on the btree cursor to estimate metadata overhead.
- Corruption paths mark the btree sick and return `-EFSCORRUPTED`.

Dependencies:
- Generic btree layer, AG/rtgroup geometry, free-space deferred freeing, rmap updates for CoW staging, transaction logging, health tracking, and errortag injection.
