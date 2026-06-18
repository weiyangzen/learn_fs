# File Research: sources/os/linux/linux/fs/xfs/xfs_trans.h

## Purpose

`xfs_trans.h` is the public internal header for the XFS transaction subsystem. It defines log item state, log item operation callbacks, transaction state, transaction flags helpers, buffer/inode transaction APIs, commit/cancel/roll entry points, and convenience helpers for transaction NOFS context handling.

## Main Contents

- Forward declarations for log, buffer, mount, inode, dquot, btree, and intent item structures used by transaction APIs.
- `struct xfs_log_item`: the common embedded object for everything that participates in the log, AIL, CIL, and transaction item lists.
- Log item flag bit numbers and `XFS_LI_FLAGS` string table:
  - `XFS_LI_IN_AIL`
  - `XFS_LI_ABORTED`
  - `XFS_LI_FAILED`
  - `XFS_LI_DIRTY`
  - `XFS_LI_WHITEOUT`
  - `XFS_LI_FLUSHING`
- `struct xfs_item_ops`: polymorphic callbacks for sizing, formatting, pin/unpin, sort, precommit, committing/committed, push, release, match, and intent lookup behavior.
- Log item operation flags:
  - `XFS_ITEM_RELEASE_WHEN_COMMITTED`
  - `XFS_ITEM_INTENT`
  - `XFS_ITEM_INTENT_DONE`
- Inline helpers `xlog_item_is_intent()` and `xlog_item_is_intent_done()`.
- Return codes for `iop_push()` implementations: success, pinned, locked, and flushing.
- `struct xfs_trans`: active transaction state, including log reservation, block and realtime reservations, flags, highest AG locked, log ticket, mount pointer, dquot accounting, superblock deltas, item list, busy extent list, deferred operation list, and saved process allocation flags.
- Exported transaction functions for allocation, extra reservation, empty allocation, superblock modification, buffer get/read/join/log/release operations, inode logging/joining, commit, roll, cancel, AIL init/destroy, buffer type tagging, and specialized inode/quota/directory allocation helpers.
- `xfs_trans_set_context()` and `xfs_trans_clear_context()` wrappers around `memalloc_nofs_save()` / `memalloc_nofs_restore()`.

## Important Design Points

- `struct xfs_log_item` is the common abstraction used by buffers, inodes, dquots, and intent/done items to participate in the same transaction and log commit machinery.
- Log item flags use atomic bit operations because AIL/CIL/writeback paths can update item state without serializing all changes under the AIL lock.
- `struct xfs_item_ops` forms the transaction subsystem's object model. Each log item type supplies the callbacks needed to format itself into the log, participate in pinning, precommit ordering, AIL pushing, and release.
- `struct xfs_trans` stores both resource reservations and logical deltas. This lets transaction code reserve conservatively up front, then release unused space and apply exact counter changes at commit/cancel time.
- The header intentionally exposes many buffer transaction operations because most XFS metadata code manipulates buffers through transaction ownership rather than direct buffer lifecycle management.
- `xfs_trans_set_sync()` is a macro that marks a transaction for synchronous log forcing after commit.

## Cross-File Relationships

- Implemented primarily by `xfs_trans.c`, plus buffer transaction code, inode item code, dquot item code, AIL code, and intent item implementations.
- Trace formatting in `xfs_trace.h` uses `XFS_LI_FLAGS` and transaction fields such as `t_ticket`, `t_flags`, and log item fields.
- Log item callbacks are consumed by CIL, AIL, log recovery, item push, and transaction precommit code.
- Buffer APIs declared here are used broadly by allocation, btree, directory, attribute, quota, log recovery, and repair code.

## Risks / Review Notes

- Any field layout or semantic change to `struct xfs_trans` has wide impact across transaction allocation, commit, quota accounting, deferred ops, and tracepoints.
- New log item types must implement `xfs_item_ops` carefully; missing sort/precommit/release behavior can lead to deadlocks, leaked locks, or incorrect log replay.
- The transaction context helpers are part of filesystem reclaim safety. Callers that allocate or duplicate transactions must preserve NOFS save/restore pairing.
- The inline single-buffer map wrappers hide `xfs_buf_map` construction; callers still need to pass correct targets, disk addresses, lengths, flags, and verifier ops.
