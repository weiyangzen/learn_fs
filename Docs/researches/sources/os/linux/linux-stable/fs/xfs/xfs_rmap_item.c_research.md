# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.c

## Purpose
Implements XFS reverse-mapping btree deferred operation log items: RUI intent items and RUD done items for data and realtime rmap updates, including logging, recovery, relogging, and deferred operation callbacks.

## Main APIs
- `xfs_rmap_defer_add` queues an rmap update intent for data or realtime metadata.
- `xfs_rui_log_space` and `xfs_rud_log_space` calculate log space for intent/done records.
- `xfs_rmap_update_defer_type` and `xfs_rtrmap_update_defer_type` define defer-op behavior.
- `xlog_rui_item_ops`, `xlog_rud_item_ops`, `xlog_rtrui_item_ops`, and `xlog_rtrud_item_ops` register recovery handlers.

## Key Behavior
RUI items log owner, physical start, file offset, length, fork/state flags, and operation type for map, shared map, unmap, shared unmap, convert, shared convert, alloc, or free. RUD items refer to a prior RUI by id and cancel the outstanding intent once the corresponding rmapbt update commits.

RUI lifetime mirrors other intent items with a two-reference model for log unpin and done-item processing. Small RUI records use slab caches, larger variable-sized records use heap allocation. RUD items release their referenced RUI when committed or aborted.

Deferred rmap work sorts intents by group, logs all map records into one intent item, creates done items, calls `xfs_rmap_finish_one`, and frees intent records after processing. Realtime rmap updates use a separate defer type so realtime metadata locking does not mix with AGF locking for data-section updates.

Recovery validates rmapbt feature availability, flags, operation type, owner inode validity, file offset/length validity, and data/realtime physical extent validity. It reconstructs `xfs_rmap_intent` items from log records, allocates recovery transactions sized for rmap btree updates, finishes intents, and captures remaining defer operations.

Relogging copies the logged map extent array into a fresh RUI to move the log tail. Realtime recovery is available only with `CONFIG_XFS_RT`; otherwise realtime RUI/RUD items are corruption.

## Dependencies
Uses log item operations, AIL, deferred operation framework, rmap btree finish helpers, recovery transaction reservations, group intent references, realtime group support, tracepoints, and slab caches.

## Failure Handling
Invalid log vector sizes, malformed flags, invalid owners, invalid extents, disabled rmapbt, or unsupported realtime recovery return `-EFSCORRUPTED`. Cursor cleanup releases AG buffers on failed data-rmap operations.
