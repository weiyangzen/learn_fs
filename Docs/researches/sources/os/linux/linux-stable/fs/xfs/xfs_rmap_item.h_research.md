# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.h

## Purpose
Declares in-core RUI/RUD log item structures and public helpers for deferred reverse-mapping btree updates.

## Main Types
`struct xfs_rui_log_item` embeds the common log item, a reference counter, next-extent counter, and variable-sized RUI log format. `struct xfs_rud_log_item` embeds a log item, references the associated RUI, and stores the RUD log format.

## Constants and API
`XFS_RUI_MAX_FAST_EXTENTS` sets the small-object slab threshold at 16 extents. The header declares RUI/RUD slab caches, `xfs_rmap_defer_add`, and log-space calculators.

## Semantics
The header documents the redo protocol for rmap updates across rolled transactions: log RUI intents first, log RUD done records with completed metadata updates, and replay unfinished rmapbt work during recovery.
