# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.c

## Scope

Implements XFS refcount btree record manipulation for reflink shared extents and in-progress CoW staging extents. The file covers AG refcount btrees and realtime-group refcount btrees, deferred intent replay, shared-range discovery, CoW staging recovery, and generic query helpers.

## APIs And Entry Points

- Lookup/read/update primitives: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_btrec_to_irec`, `xfs_refcount_check_irec`, `xfs_rtrefcount_check_irec`, `xfs_refcount_get_rec`, `xfs_refcount_insert`.
- Deferred operation finishers: `xfs_refcount_finish_one` for AG refcount updates and `xfs_rtrefcount_finish_one` for realtime-group refcount updates.
- Intent producers: `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`.
- Query/recovery helpers: `xfs_refcount_find_shared`, `xfs_refcount_recover_cow_leftovers`, `xfs_refcount_has_records`, `xfs_refcount_query_range`.
- Slab lifecycle: `xfs_refcount_intent_init_cache`, `xfs_refcount_intent_destroy_cache`.

## Data Model

- Refcount records are represented by `struct xfs_refcount_irec`: start block, block count, refcount, and domain.
- Domains distinguish normal shared extents from CoW staging extents. Shared records must have `rc_refcount >= 2`; CoW-domain records must have `rc_refcount == 1`.
- Gaps in the shared-domain refcount btree are interpreted as allocated extents with refcount 1 when the caller is adjusting a mapped file extent.
- CoW staging allocations are deliberately stored as refcount-1 records in a separate key domain so crash recovery can find and free orphaned CoW blocks.

## Control Flow

- Boundary preparation:
  - `xfs_refcount_split_extent` splits any record crossing the start or end of an adjustment range.
  - `xfs_refcount_find_left_extents` and `xfs_refcount_find_right_extents` locate adjacent shoulder records and synthesize refcount-1 records for gaps inside the target range.
- Merge phase:
  - `xfs_refc_want_merge_center`, `xfs_refc_want_merge_left`, and `xfs_refc_want_merge_right` decide whether the adjusted center range can merge with adjacent records without exceeding `XFS_REFC_LEN_MAX`.
  - `xfs_refcount_merge_extents` performs center, left, or right merges before modifying middle extents.
- Adjustment phase:
  - `xfs_refcount_adjust_extents` increments/decrements middle shared extents, inserts records for refcount-1 gaps that become shared, removes records that drop to refcount 1, and schedules frees when decrementing below 1.
  - `xfs_refcount_still_have_space` conservatively limits work per transaction so deferred processing can continue safely.
  - `xfs_refcount_continue_op` and `xfs_rtrefcount_continue_op` rewrite unfinished intents to start at the next unprocessed group block.
- CoW phase:
  - `xfs_refcount_adjust_cow` uses the same split/merge boundary machinery but then calls `xfs_refcount_adjust_cow_extents`, which requires exact non-overlap on allocation and exact matching record deletion on free.
  - `xfs_refcount_recover_cow_leftovers` scans CoW-domain records after mount, queues each orphan, and later frees both the refcount record and the underlying blocks.

## Dependencies

- Uses generic XFS btree APIs, refcount btree cursor ops, realtime refcount cursor ops, allocation/free deferred extent machinery, transaction reservation state, reverse-map updates for CoW staging, group/perag/rtgroup helpers, health marking, tracepoints, and error injection tags.
- Depends on `xfs_refcount_encode_startblock` from the header for domain-aware key encoding.
- Realtime support depends on `xfs_rtgroup_lock`, `xfs_rtgroup_trans_join`, `xfs_rtrefcountbt_init_cursor`, and realtime block conversion/verification helpers.

## Invariants And Risks

- Shared and CoW domains must not be merged together; the separate domain checks and COW flag encoding preserve this.
- Refcount records must never cross the range boundaries before middle adjustment; otherwise decrement/free logic can corrupt ownership accounting.
- `XFS_REFC_REFCOUNT_MAX` records are pinned at max and skipped during adjustment.
- Transaction continuation depends on accurate `ri_blockcount` reduction and startblock rewrite.
- CoW recovery intentionally uses an empty transaction for the scan phase to avoid refcountbt buffer lock deadlocks, then frees leftovers one transaction at a time.
