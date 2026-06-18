# File Research: sources/local-fs/xfsprogs/libxfs/xfs_defer.h

## Purpose

`xfs_defer.h` declares the data structures and APIs for XFS deferred operations and log intent/done orchestration.

## Key Contents

`struct xfs_defer_pending` tracks one batch of deferred work: list linkage, work item list, intent and done log items, operation type, item count, and flags. `XFS_DEFER_PAUSED` marks work that has an intent but should not be finished yet.

`struct xfs_defer_op_type` describes a deferred operation implementation with callbacks to create/abort intents, create done items, finish/cancel work items, clean up per-finish state, recover work, and relog intents. The header declares the concrete defer types for bmap, refcount, realtime refcount, rmap, realtime rmap, extent free, AGFL free, realtime extent free, attr, and exchange mapping work.

`struct xfs_defer_resources` captures held buffers and inodes across transaction rolls. `struct xfs_defer_capture` stores detached deferred-op state, transaction flags, block reservations, log reservation, and held resources so recovery can commit and resume work later.

The exported APIs add work, finish/cancel/move deferred ops, finish a single pending item, capture/continue/abort recovery chains, release captured resources, start/cancel/finish recovery work, initialize/destroy item caches, pause/unpause items, and add merge barriers.

## Dependencies and Risks

The header ties together transactions, log items, btree cursors, buffers, inodes, and operation-specific intent modules. Correct use requires permanent log reservations, valid callback tables, and careful ownership of captured buffers/inodes across transaction commit and recovery continuation.
