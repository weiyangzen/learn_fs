# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans.h

## Purpose
Declares the kernel-only XFS transaction subsystem interfaces, transaction object layout, log item layout, log item operation callbacks, transaction buffer/inode APIs, transaction allocation helpers, and NOFS context helpers.

## Main Types
- `struct xfs_log_item` is the common in-core object embedded by all loggable XFS metadata items. It tracks AIL linkage, transaction linkage, LSN, log/AIL pointers, item type, flags, attached buffer, buffer item list, item ops, CIL list/vector state, CIL sequence, and commit ordering id.
- `struct xfs_item_ops` defines callbacks for log item sizing, formatting, pin/unpin, sorting, precommit, committing/committed completion, AIL push, release, matching, and intent lookup.
- `struct xfs_trans` is the active transaction handle. It tracks log reservation/count/ticket, block and realtime extent reservations and use, transaction flags, highest locked AGF, mount pointer, quota accounting, superblock deltas, item list, busy extent list, deferred operation list, and saved process allocation flags.

## Important Flags and Helpers
- Log item flags include `IN_AIL`, `ABORTED`, `FAILED`, `DIRTY`, `WHITEOUT`, and `FLUSHING`.
- Log item op flags distinguish release-on-commit items, intent items, and intent-done items.
- `xlog_item_is_intent` and `xlog_item_is_intent_done` classify intent log items.
- AIL push return values include success, pinned, locked, and flushing.
- `xfs_trans_set_sync` marks a transaction synchronous.
- `xfs_trans_set_context` and `xfs_trans_clear_context` wrap `memalloc_nofs_save/restore` around transaction lifetime.

## Exported Interfaces
The header exposes:
- Transaction allocation/reservation: `xfs_trans_alloc`, `xfs_trans_reserve_more`, `xfs_trans_alloc_empty`.
- Superblock delta updates: `xfs_trans_mod_sb`.
- Buffer acquisition/read helpers: `xfs_trans_get_buf_map`, inline `xfs_trans_get_buf`, `xfs_trans_read_buf_map`, inline `xfs_trans_read_buf`, `xfs_trans_getsb`, and `xfs_trans_getrtsb`.
- Buffer transaction operations: release, join, detach, hold, hold release, invalidate, inode buffer marking, stale inode buffer marking, ordered buffer marking, dquot buffer marking, inode allocation buffer marking, buffer logging, dirty marking, dirty test, buffer type setting/copying.
- Inode transaction operations: `xfs_trans_ijoin` and `xfs_trans_log_inode`.
- Transaction completion: `xfs_trans_commit`, `xfs_trans_roll`, `xfs_trans_roll_inode`, and `xfs_trans_cancel`.
- AIL lifecycle: `xfs_trans_ail_init` and `xfs_trans_ail_destroy`.
- Higher-level allocation helpers for inode updates, incremental inode reservations, inode create, inode change, and directory updates.
- `xfs_trans_cache` as the transaction slab cache.

## Integration
This header is the shared transaction contract for XFS metadata code. Implementations in transaction, buffer item, inode item, quota, defer, log, and AIL code depend on these structures and callbacks. The inline buffer helpers standardize single-buffer map setup for callers while routing actual behavior through map-based APIs.

## Risk Notes
`struct xfs_log_item` and `struct xfs_trans` are central cross-module data structures. Changes to fields, flags, callback semantics, or reservation accounting can affect journaling, AIL tracking, CIL formatting, metadata locking, quota behavior, and shutdown correctness. The NOFS context helpers are also important because transaction code often runs while holding filesystem locks.
