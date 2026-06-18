# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.h

## Purpose
Declares in-core CUI/CUD log item structures and public helpers for deferred refcount btree updates.

## Main Types
`struct xfs_cui_log_item` embeds a log item, reference count, next-extent counter, and variable-sized CUI log format. `struct xfs_cud_log_item` embeds a log item, points to the associated CUI, and stores the CUD log format.

## Constants and API
`XFS_CUI_MAX_FAST_EXTENTS` sets the small-object slab threshold at 16 extents. The header declares CUI/CUD slab caches, `xfs_refcount_defer_add`, and log-space calculators for intent and done items.

## Semantics
The header documents the redo protocol: CUI intent items are logged in the first transaction of a rolled series, CUD done items are logged with the metadata updates, and recovery replays unfinished refcount updates after a crash.
