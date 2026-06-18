# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount.c

Implements XFS reflink reference count record operations for both AG refcount btrees and realtime refcount btrees. It manages shared-block refcounts, CoW staging extents, deferred refcount intents, record validation, range queries, and crash recovery of orphaned CoW allocations.

Core behavior:
- Provides lookup helpers `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, and `xfs_refcount_lookup_eq` over `(domain, startblock)`.
- Converts and validates on-disk refcount records with `xfs_refcount_btrec_to_irec`, `xfs_refcount_check_irec`, and `xfs_rtrefcount_check_irec`.
- Maintains strict domain semantics: shared records must have refcount >= 2; CoW staging records must have refcount exactly 1.
- Uses `xfs_refcount_insert`, internal update/delete helpers, and btree sickness marking on impossible cursor states or corrupt records.

Reference adjustment algorithm:
- `xfs_refcount_adjust` handles shared-domain increments/decrements.
- It first splits records crossing adjustment boundaries, then attempts left/right/center merges, then updates interior records.
- Gaps in the shared refcount btree are treated as implicit refcount-1 extents because allocated unshared blocks are not stored in refcountbt.
- Decrementing a record to refcount 1 deletes it from refcountbt; decrementing implicit or explicit refcount-1 space schedules block freeing.
- `xfs_refcount_still_have_space` conservatively limits how many record changes fit in the current transaction, allowing deferred continuations.

Deferred operation handling:
- `xfs_refcount_finish_one` processes AG refcount intents and reuses a refcountbt cursor while operations remain in the same AG.
- `xfs_rtrefcount_finish_one` performs the same operation for realtime groups, using rtgroup refcount locks and realtime block conversions.
- `__xfs_refcount_add`, `xfs_refcount_increase_extent`, and `xfs_refcount_decrease_extent` enqueue deferred refcount changes only when reflink is enabled.
- Continuation helpers update the intent startblock/blockcount after partial completion and verify the remaining range.

CoW staging support:
- CoW allocations are stored in the CoW refcount domain as refcount-1 records so that crash recovery can find allocated-but-unmapped CoW blocks.
- `xfs_refcount_alloc_cow_extent` records a CoW staging extent and creates an rmap owned by `XFS_RMAP_OWN_COW`.
- `xfs_refcount_free_cow_extent` removes the rmap and queues removal of the CoW refcount record.
- `xfs_refcount_recover_cow_leftovers` scans CoW-domain records at mount/recovery time, queues them for deletion, and frees the orphaned blocks.

Query and scan utilities:
- `xfs_refcount_find_shared` locates the first shared subrange in a physical extent and can optionally extend through contiguous shared records.
- `xfs_refcount_has_records` reports none/full/partial record coverage for a key range.
- `xfs_refcount_query_range` wraps generic btree range queries and validates each returned record.

Important interactions:
- Uses `xfs_refcount_btree.c` cursor and btree operations for AG refcountbt.
- Uses realtime refcount btree support through `xfs_rtrefcount_btree.h`.
- Calls rmap helpers to track CoW staging ownership.
- Calls deferred free helpers when refcount decreases release blocks.
- Marks AG/rtgroup btrees sick on corruption through btree health APIs.

Risk points:
- Boundary splitting, synthesized implicit refcount-1 records, and merge logic are correctness-critical.
- Shared and CoW domains share one encoded startblock namespace, so domain encoding/decoding must remain consistent.
- Transaction space estimation is intentionally conservative; wrong estimates can force continuation or risk reservation exhaustion.
