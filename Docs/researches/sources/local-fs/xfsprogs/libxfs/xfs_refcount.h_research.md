# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount.h

Public interface for XFS refcount operations shared by libxfs users. It declares refcountbt lookup/query/update APIs, deferred intent types, CoW staging helpers, validation helpers, and cache lifecycle functions.

Key declarations:
- Lookup and read APIs: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`.
- `xfs_refcount_encode_startblock` stores the CoW-domain bit in the on-disk startblock key for non-shared domains.
- Intent enum values: increase, decrease, allocate CoW, free CoW.
- `struct xfs_refcount_intent` carries deferred operation type, group, startblock, blockcount, and realtime flag.
- Domain checker `xfs_refcount_check_domain` enforces CoW refcount 1 and shared refcount >= 2.

Exported workflows:
- `xfs_refcount_increase_extent` and `xfs_refcount_decrease_extent` enqueue file extent refcount adjustments.
- `xfs_refcount_finish_one` and `xfs_rtrefcount_finish_one` execute deferred AG or realtime refcount intents.
- `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`, and `xfs_refcount_recover_cow_leftovers` manage CoW staging records.
- `xfs_refcount_find_shared` supports shared-range discovery for reflink/COW decisions.
- `xfs_refcount_has_records` and `xfs_refcount_query_range` expose record coverage/query functionality.

Notable constants:
- `XFS_REFCOUNT_ITEM_OVERHEAD` is the conservative per-record transaction log space estimate used by the implementation.

Dependencies:
- Uses `struct xfs_btree_cur`, `struct xfs_bmbt_irec`, `struct xfs_refcount_irec`, `struct xfs_perag`, and `struct xfs_rtgroup`.
- Exposes `xfs_refcount_intent_cache` for deferred-item allocation.
