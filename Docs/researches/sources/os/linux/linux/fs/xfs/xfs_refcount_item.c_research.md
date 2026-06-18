# File Research: sources/os/linux/linux/fs/xfs/xfs_refcount_item.c

## Role

Deferred log intent/done item implementation for refcount btree updates. It supports crash-recoverable refcount changes for reflink/CoW on data and realtime devices.

## Main Responsibilities

- Defines caches for CUI/CUD log items: `xfs_cui_cache`, `xfs_cud_cache`.
- Manages CUI lifecycle through allocation, formatting, unpin, release, AIL deletion, and variable-size freeing.
- Manages CUD lifecycle and links done items back to their CUI intent.
- Logs deferred refcount intents with `xfs_refcount_update_log_item`.
- Adds work to deferred operation queues through `xfs_refcount_defer_add`, splitting realtime and data-section work into separate defer types.
- Finishes deferred work using `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`.
- Recovers CUIs from log items, validates physical extents, rebuilds deferred work, allocates recovery transactions, and commits or captures remaining deferred work.
- Relogs intent items to advance the log tail.
- Provides recovery handlers for CUI/CUD and realtime CUI/CUD log item types.

## Important Types and Operations

- CUI: refcount update intent, containing one or more `xfs_phys_extent` entries.
- CUD: done item canceling a previous CUI by ID.
- Supported intent types include increase, decrease, alloc-COW, and free-COW.
- Realtime variants use `XFS_LI_CUI_RT` and `XFS_LI_CUD_RT`; if realtime support is not compiled in, recovered realtime items are treated as corruption.

## Consistency Checks

Recovery rejects CUIs if reflink is unavailable, flags are invalid, type bits are unknown, or extents fail data/realtime extent verification. On corruption, it reports with `XFS_CORRUPTION_ERROR`.

## Dependencies

Uses defer ops, transactions, log recovery, refcount btree helpers, AG/RT group abstractions, btree cursors, tracepoints, and realtime refcount support.
