# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_item.c

Implements logged deferred bmap update intent/done items: BUI and BUD, used to redo mapping and unmapping of inode bmbt extents across transaction rolls and log recovery.

Key elements:
- Defines BUI/BUD slab caches and log item ops.
- BUI lifecycle handles allocation, formatting, sizing, unpin, release, match, relogging, and recovery copy-in.
- BUD lifecycle handles formatting, sizing, release, and linking to the originating BUI.
- `xfs_bmap_update_log_item` records owner inode, start block, file offset, length, map/unmap type, unwritten state, attr fork, and realtime flags into the BUI extent slot.
- `xfs_bmap_update_create_intent` optionally sorts bmap intents by owner inode and logs them into a BUI.
- `xfs_bmap_defer_add` takes a group intent reference, precharges `i_delayed_blks` for map operations, traces, and queues deferred bmap work.
- `xfs_bmap_update_cancel_item` reverses map precharge, drops group intent, and frees the intent.
- `xfs_bmap_update_finish_item` calls `xfs_bmap_finish_one`; unfinished unmaps return `-EAGAIN` for continuation.
- `xfs_bui_validate` checks recovered BUI format, flags, operation type, owner inode, file extent range, and data/realtime physical extent range.
- `xfs_bui_recover_work` reconstructs `xfs_bmap_intent`, igets the owner inode, restores fork/type/extent state, takes group intent, and queues recovered work.
- `xfs_bmap_recover_work` allocates a recovery transaction, locks/joins the inode, verifies realtime consistency, reserves extent-count growth, finishes the intent, and captures/commits defer ops.
- Recovery pass2 creates incore BUIs from logged BUI formats and releases BUIs when matching BUDs are found.

Dependencies:
- Uses XFS defer ops, log item/recovery framework, bmap finish helpers, group intent references, inode recovery iget, and transaction reservations.

Research notes:
- `XFS_BUI_MAX_FAST_EXTENTS` is one, so each BUI carries one mapping update.
- `i_delayed_blks` precharge prevents transient `stat` under-reporting during out-of-place remap operations.
- Group intent references bridge bmap work that can enqueue rmap/refcount work across transaction rolls.
- Recovery rejects BUI records with unsupported flags or invalid extents before touching metadata.
