# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.h

Public interface for refcount btree operations and deferred refcount intents.

Key contents:
- Declares lookup/get/insert helpers for refcount btree cursors.
- Defines `xfs_refcount_encode_startblock`, which folds the refcount domain into the startblock key using `XFS_REFC_COWFLAG`.
- Defines deferred intent types: increase, decrease, allocate CoW, free CoW.
- Defines `struct xfs_refcount_intent`, carrying group, operation type, startblock, block count, and realtime flag.
- Provides `xfs_refcount_check_domain`, enforcing that CoW records have refcount 1 and shared records have refcount at least 2.
- Exposes high-level APIs for file extent refcount changes, CoW staging changes, CoW recovery, shared-range search, record existence checks, and range queries.
- Defines `XFS_REFCOUNT_ITEM_OVERHEAD` for transaction-space estimation during deferred refcount work.
- Declares slab cache lifecycle for refcount intents.

Design notes:
- The header abstracts both regular AG refcount and realtime refcount users.
- Domain validation is intentionally inline because both verifier and mutation code need the same invariant.
