# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.h

## Scope

Public interface for XFS refcount operations, refcount deferred intents, refcount record validation, query callbacks, and CoW staging helpers.

## APIs And Types

- Declares btree lookup/read APIs: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`.
- Defines `xfs_refcount_encode_startblock`, which encodes the CoW-domain bit into the on-disk startblock key for non-shared domains.
- Defines `enum xfs_refcount_intent_type`: increase, decrease, allocate CoW, free CoW.
- Defines `struct xfs_refcount_intent`, carrying deferred op type, target group, start block, block count, and realtime flag.
- Defines `xfs_refcount_check_domain`, enforcing that CoW records have refcount 1 and shared records have refcount at least 2.
- Declares deferred finishers for normal and realtime refcount trees.
- Declares CoW staging APIs, shared-range discovery, CoW leftover recovery, record packing/query helpers, validation helpers, and slab-cache lifecycle.

## Notable Constants

- `XFS_REFCOUNT_ITEM_OVERHEAD` estimates log space consumed per refcount update when deciding whether to continue an operation in the current transaction.
- `XFS_REFCOUNT_INTENT_STRINGS` maps intent types to trace/log strings.

## Dependencies

- Exposes types from transactions, mounts, per-AG state, btree cursors, bmap extents, realtime groups, btree records, and XFS record-packing results.

## Invariants And Risks

- `xfs_refcount_encode_startblock` treats any domain that is not explicitly shared as CoW-like for low-level btree range queries. Callers must set domains deliberately.
- The header codifies the semantic split between shared extents and CoW staging records; callers that bypass `xfs_refcount_check_domain` can accept impossible records.
