# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.c

## Purpose
Implements XFS refcount btree deferred operation log items: CUI intent items and CUD done items for data and realtime refcount updates, including formatting, lifecycle, recovery, relogging, and defer-op integration.

## Main APIs
- `xfs_refcount_defer_add` queues a refcount intent onto the correct data or realtime defer type.
- `xfs_cui_log_space` and `xfs_cud_log_space` compute log space for intent/done items.
- `xfs_refcount_update_defer_type` and `xfs_rtrefcount_update_defer_type` provide deferred operation callbacks.
- `xlog_cui_item_ops`, `xlog_cud_item_ops`, `xlog_rtcui_item_ops`, and `xlog_rtcud_item_ops` register log recovery handlers.

## Key Behavior
CUI items record one or more physical extents plus operation flags for increase, decrease, CoW allocation, or CoW free. CUD items refer back to a CUI by id and release the intent when the corresponding updates have completed.

CUI lifetime uses a two-reference model so both log unpin and CUD processing can race safely with AIL insertion. Large CUI items are heap allocated; small items use a slab cache. CUD items are released when committed and drop their referenced CUI.

Deferred refcount work sorts by allocation group or realtime group, logs intents, creates done items, calls `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`, and requeues partially finished increase/decrease operations with `-EAGAIN`.

Recovery validates reflink feature availability, extent flags, operation types, and data/realtime extent ranges before reconstructing deferred work. Recovery allocates an itruncate-style reservation sized for refcount btree splits, finishes recovered intents, captures remaining defer work, and treats malformed intents as corruption.

Relogging copies extent arrays into a new CUI to push the log tail forward. Realtime CUI/CUD recovery is compiled only with `CONFIG_XFS_RT`; without it, realtime refcount intent records are reported as corruption.

## Dependencies
Uses XFS log item operations, AIL, deferred operation framework, refcount btree finish/recovery helpers, transaction reservation recovery helpers, group intent references, realtime group support, tracepoints, and slab caches.

## Failure Handling
Malformed log vectors, invalid flags, unsupported reflink state, invalid extents, or realtime intents without realtime support return `-EFSCORRUPTED`. Finish cleanup deletes btree cursors and releases AG buffers on error.
