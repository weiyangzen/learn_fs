# File Research: sources/local-fs/xfsprogs/libxfs/xfs_defer.c

## Purpose

`xfs_defer.c` implements XFS deferred operation orchestration: grouping work items, logging intent and done items, rolling transactions, replaying recovered intents, capturing deferred state during recovery, preserving held resources across rolls, and managing deferred-operation caches.

## Main Behavior

Deferred work is tracked in `xfs_defer_pending` records grouped by operation type. Work enters a transaction’s deferred list, gets batched up to the op type’s `max_items`, and later has an intent item logged before the transaction rolls. Finishing creates a done item, calls the operation type’s `finish_item` callback for each work item, and frees the pending record when complete.

`xfs_defer_finish_noroll` is the main engine. It repeatedly creates intents for intake work, isolates paused items, moves work to a pending list, rolls when intents exist, relogs older intents so they do not pin the log tail, and finishes one pending item at a time. If a callback returns `-EAGAIN`, the unfinished work item is put back, a replacement intent is logged, and processing continues in a fresh transaction. Fatal errors abort intents, cancel work, and force shutdown.

The file preserves resources that must survive transaction rolls. `xfs_defer_save_resources` records held buffers and inodes from transaction items; `xfs_defer_restore_resources` rejoins and reholds them after a roll. Recovery support can capture a chain of deferred ops with block/log reservations and held resources, commit it, then continue it later via `xfs_defer_ops_continue`.

It also provides barrier deferred ops to prevent adjacent work from being merged, APIs to add/cancel/move deferred work, start/cancel/finish recovery work, pause/unpause items, release captured resources, and initialize/destroy caches for defer, rmap, refcount, bmap, extent-free, attr, and exchange-mapping intent items.

## Dependencies and Risks

This file depends on transaction internals, log items, AIL/log-tail behavior, btree cursors, rmap/refcount/bmap/attr/exchmaps intent modules, inode and buffer locking, and shutdown semantics. Risky areas are intent/done atomicity across transaction rolls, `-EAGAIN` continuation correctness, preserving enough reservation to log replacement intents, resource hold/rejoin ordering, recovery capture lifetime, and paused items delaying dependent work.
