# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_cil.c

## Purpose

`xfs_log_cil.c` implements the XFS Committed Item List. The CIL aggregates committed transaction items in memory into checkpoint contexts, supports relogging of frequently modified metadata, pushes checkpoints asynchronously or synchronously to the core log, and completes checkpoints by moving committed items to the AIL and unpinning them.

It sits between transaction commit and the lower-level iclog writer in `xfs_log.c`.

## Core Model

The active CIL context (`struct xfs_cil_ctx`) collects formatted log vectors, busy extents, and per-CPU insertion state. Transaction commit formats dirty log items into reusable or shadow log vector buffers, inserts them into the active CIL, steals unused transaction reservation into the checkpoint ticket, and may trigger a background push when thresholds are crossed.

Push work switches to a fresh CIL context, builds an ordered log vector chain from the old context, writes a checkpoint start/header and item payloads, writes an ordered commit record, and attaches completion callbacks to the commit iclog.

## Formatting and Insertion

`xlog_cil_alloc_shadow_bufs` preallocates or resizes per-item shadow log vectors before taking the CIL context lock. This avoids memory reclaim deadlocks while a push needs to make progress.

`xlog_format_start` and `xlog_format_commit` build aligned log iovec regions with embedded `xlog_op_header` records. They ensure payload alignment, zero padding, region type assignment, op header length, and vector byte accounting.

`xlog_cil_insert_format_items` formats dirty transaction items into reusable or shadow log vectors. `xfs_cil_prepare_item` pins newly inserted items, swaps old vectors into shadow storage when relogging, updates diff accounting, and records the first CIL sequence on the item.

`xlog_cil_insert_items` performs per-CPU accounting, busy extent aggregation, reservation stealing, CIL item ordering, and transaction ticket reservation checks. It uses per-CPU counters below the soft threshold and transitions to atomic accounting near or above the CIL limit.

## Push Path

`xlog_cil_push_work` is the main checkpoint push worker. It:

- Allocates a new context and ticket under `GFP_NOFS` constraints.
- Takes the CIL context write lock and aggregates per-CPU state.
- Skips if the CIL is empty or the requested sequence was already pushed.
- Adds the old context to the committing list before switching contexts.
- Builds and sorts the log vector chain by transaction order id.
- Builds a checkpoint transaction header.
- Writes the start record and item chain via `xlog_write`.
- Writes the commit record via `xlog_write_one_vec`.
- Ensures prior iclogs are completed if the checkpoint spans multiple iclogs.
- Marks commit iclog with flush/FUA requirements and optionally forces it stable for async flush semantics.
- Releases the commit iclog and ungrants the checkpoint ticket.

Whiteout handling lets paired intent/done items from the same checkpoint avoid unnecessary journal writes. `xlog_cil_process_intents` marks the intent item as whiteout and releases the done item when the intent and done are atomic within the current checkpoint.

## Completion Path

`xlog_cil_set_ctx_write_state` records checkpoint `start_lsn` on the first write and `commit_lsn` on the commit write. It also attaches the context callback to the commit iclog before publishing the commit LSN so callback order matches commit record order.

`xlog_cil_process_committed` drains completed contexts from iclog callback lists. `xlog_cil_committed` inserts items into the AIL, clears busy extents, handles discard, removes the context from the committing list, frees log vectors, and releases the context.

`xlog_cil_ail_insert` updates the AIL head LSN to the commit record LSN, returns grant space in the correct order, runs `iop_committed`, bulk-inserts normal items at the checkpoint start LSN, handles special item LSNs individually, and unpins items. Abort mode skips AIL insertion and unpins with abort semantics.

## Forcing and Throttling

`xlog_cil_push_background` queues background pushes when the soft CIL space limit is exceeded and throttles transaction commits above the hard blocking limit.

`xlog_cil_push_now` queues immediate pushes for log force and flush operations. Sync callers flush prior push work to reduce wait time; async flush requests set `xc_push_commit_stable` so the push worker forces the commit record to stable storage.

`xlog_cil_force_seq` ensures a requested checkpoint sequence has been pushed far enough to expose a commit LSN, waiting for lower or equal sequence commits as needed. It returns the commit LSN used by `xfs_log_force_seq` to flush the corresponding iclog.

## Initialization and Teardown

`xlog_cil_init` allocates `struct xfs_cil`, creates a bounded push workqueue, allocates per-CPU CIL structures, initializes locks and waitqueues, installs the first context, and attaches the CIL to the log.

`xlog_cil_init_post_recovery` allocates the first checkpoint ticket after recovery has established log head/tail geometry. `xlog_cil_destroy` frees the active context, ticket, per-CPU state, workqueue, and CIL.

## Research Notes

The file’s central correctness requirements are strict checkpoint ordering, accurate reservation stealing, avoiding memory reclaim deadlocks, preserving metadata/log stable-storage ordering with flush/FUA flags, and completing callbacks in the same order as commit records. The CIL is deliberately optimized for repeated relogging while bounding pinned memory and checkpoint size.
