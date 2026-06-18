# File Research: sources/os/linux/linux/fs/xfs/xfs_log_cil.c

## Purpose

`xfs_log_cil.c` implements the XFS Committed Item List (CIL), the delayed logging subsystem that aggregates committed transaction items into checkpoint contexts before writing them to the physical log. It handles per-transaction log item formatting, shadow log vector buffering, per-CPU accumulation, checkpoint context switching, background and forced pushes, strict checkpoint write ordering, commit-record stable-storage semantics, post-commit AIL insertion, busy extent cleanup, and CIL initialization/destruction.

## Major Responsibilities

- Allocate checkpoint tickets that steal reservation space from committing transactions instead of independently reserving log space.
- Track whether log items are already in the current checkpoint sequence.
- Allocate and maintain shadow log-vector buffers to avoid memory allocation while the CIL context lock is held.
- Format dirty transaction items into flat log vectors with aligned opheader-prefixed regions.
- Insert items into the active CIL context, pinning newly added items and accounting only the delta when relogging existing items.
- Aggregate per-CPU CIL space, busy extents, and item lists into the checkpoint context during a push.
- Switch from the current active context to a new empty context while the old one is written out.
- Build checkpoint transaction headers, write checkpoint data, then write ordered commit records.
- Attach checkpoint callbacks to commit iclogs so completion processing can move items into the AIL and unpin them.
- Force CIL sequences for `fsync`/log-force callers and return the commit LSN that the log manager must force.
- Process intent/done pairs within the same checkpoint by whiteing out redundant intent logging.

## CIL Context Lifecycle

1. `xlog_cil_init()` allocates `struct xfs_cil`, a bounded push workqueue, per-CPU tracking areas, locks/wait queues, and the first context.
2. `xlog_cil_init_post_recovery()` allocates the initial checkpoint ticket after recovery establishes log head/tail state.
3. Transaction commits call `xlog_cil_commit()` under a read lock on `xc_ctx_lock`.
4. Items are formatted, inserted into the active context, and the transaction ticket donates reservation space to the checkpoint ticket.
5. `xlog_cil_push_background()` queues push work when soft/hard CIL space limits are reached.
6. `xlog_cil_push_work()` takes the write lock, aggregates per-CPU state, links the old context on `xc_committing`, switches to a new context, and writes the old context to the log.
7. The commit iclog callback eventually calls `xlog_cil_process_committed()`, which invokes `xlog_cil_committed()` and frees the old context after AIL/busy-extent cleanup.
8. `xlog_cil_destroy()` frees the active empty context, per-CPU storage, workqueue, and CIL structure.

## Log Vector Formatting

- `xlog_cil_alloc_shadow_bufs()` runs before taking the CIL context lock. It asks each dirty item for `iop_size()`, allocates or reuses `li_lv_shadow`, accounts alignment, and handles ordered items by setting `lv_buf_used` to `XFS_LOG_VEC_ORDERED`.
- `xlog_format_start()` initializes a region iovec and embedded `xlog_op_header`, aligning payload start to 8 bytes.
- `xlog_format_commit()` rounds payload length, zeroes padding, records opheader length, advances `lv_buf_used`, increments `lv_bytes`, and advances the formatter index.
- `xlog_cil_insert_format_items()` either reuses the existing log vector when the shadow fits, swaps to the shadow buffer, or handles ordered items without data regions. It then calls each item’s `iop_format()`.
- `xfs_cil_prepare_item()` accounts new vs. replaced log-vector bytes, pins first-time CIL items, swaps old vectors into `li_lv_shadow`, attaches the new vector to the item, and records the first checkpoint sequence in `li_seq`.

## Space Accounting and Limits

The CIL uses dynamic reservation stealing. `xlog_cil_insert_items()` subtracts consumed item bytes and checkpoint overhead from the committing transaction ticket and adds reserved space to the checkpoint context ticket through per-CPU accounting.

Important mechanisms:

- `XLOG_CIL_SPACE_LIMIT(log)` is the smaller of one-eighth of log space and 16 times the iclog window, limiting memory pinned by delayed logging while preserving relogging efficiency.
- `XLOG_CIL_BLOCKING_SPACE_LIMIT(log)` is twice the background limit and triggers commit throttling.
- `XLOG_CIL_PCP_SPACE` enables low-contention per-CPU space accounting below the soft limit; once the soft limit is crossed, `xlog_cil_insert_pcp_aggregate()` folds per-CPU counts into the atomic global counter.
- `xc_iclog_hdrs` tracks remaining expected iclog header reservations; commits steal more header/split reservation space when needed or when over the hard limit.
- `xlog_cil_over_hard_limit()` also treats active push waiters as a hard-limit condition, so once throttling begins it remains enforced until the context switch wakes waiters.

## Checkpoint Push Flow

`xlog_cil_push_work()` is the main push worker:

- Runs under `memalloc_nofs_save()` to avoid filesystem reclaim recursion.
- Allocates a new context and ticket before taking `xc_ctx_lock` exclusively.
- Aggregates per-CPU state into the old context with `xlog_cil_push_pcp_aggregate()`.
- Skips if the CIL is empty or the requested sequence was already pushed.
- Adds the old context to `xc_committing` before emptying/switching it so waiters can distinguish "push in progress" from "nothing to do".
- Builds the log-vector chain from CIL items via `xlog_cil_build_lv_chain()`, moving whiteout items aside.
- Switches to the new active context with `xlog_cil_ctx_switch()`.
- Sorts log vectors by transaction order id using `xlog_cil_order_cmp()`.
- Builds and prepends a checkpoint transaction header via `xlog_cil_build_trans_hdr()`.
- Writes checkpoint data through `xlog_cil_write_chain()`, then writes the commit record through `xlog_cil_write_commit_record()`.
- Waits for prior iclogs if the checkpoint spans multiple iclogs, sets preflush/FUA as needed, releases the commit iclog, cleans whiteouts, and ungrants the checkpoint ticket.

## Ordering Rules

The file enforces ordering at several layers:

- Start records and commit records are strictly ordered by checkpoint sequence using `xlog_cil_order_write()`, `xc_start_wait`, and `xc_commit_wait`.
- `xlog_cil_set_ctx_write_state()` records the start LSN on the first write and the commit LSN on the commit-record write. It attaches the checkpoint callback to the commit iclog before publishing `commit_lsn`.
- Checkpoint callbacks are attached to iclogs in commit-record order so completion processing sees checkpoints in correct order.
- If a checkpoint spans multiple iclogs, push work waits on the previous iclog and marks the commit iclog with `NEED_FLUSH` so stable-storage ordering is preserved.
- Commit iclogs always get `NEED_FUA`; asynchronous flush requests can force the active commit iclog to `WANT_SYNC` so the commit record reaches stable storage without a later force.

## AIL and Completion Processing

`xlog_cil_process_committed()` drains a list of completed CIL contexts from iclog callbacks. `xlog_cil_committed()` then:

- Detects abort state from log shutdown and wakes push waiters early.
- Calls `xlog_cil_ail_insert()` to run item committed callbacks and insert items into the AIL in batches.
- Sorts and clears busy extents, optionally issuing discard if enabled and not aborting.
- Removes the context from `xc_committing`.
- Frees log vectors.
- Either schedules discard ownership by keeping the context alive or frees the context immediately.

`xlog_cil_ail_insert()` updates the AIL head LSN to the checkpoint commit LSN before returning grant space. It uses a write memory barrier paired with grant-space reads to avoid transiently overestimating available log space. Items with `XFS_ITEM_RELEASE_WHEN_COMMITTED` are released immediately; unusual item LSNs bypass bulk insertion; abort paths set `XFS_LI_ABORTED` and unpin without AIL insertion.

## Intent Whiteouts

`xlog_cil_process_intents()` optimizes transactions that contain intent-done items whose related intent was first committed in the current checkpoint. In that case both records are unnecessary for recovery because the operation is atomic within the checkpoint:

- The related intent item is marked `XFS_LI_WHITEOUT`.
- Its log vector bytes are counted as released space.
- The intent-done item is removed from the transaction and released.
- `xlog_cil_build_lv_chain()` later skips whiteout items, and `xlog_cil_cleanup_whiteouts()` unpins them as aborted/skipped work.

## Force APIs

- `xlog_cil_flush()` triggers an asynchronous push of the current sequence with stable-commit semantics and forces the log if the CIL is already empty but a previous checkpoint might still sit in an active iclog.
- `xlog_cil_force_seq()` queues a push for the requested sequence, waits for prior or matching committing contexts to publish a commit LSN, retries races where the current context has not started pushing yet, and returns the commit LSN for the log-force layer. During shutdown it returns zero rather than `NULLCOMMITLSN` so the caller still exercises iclog error handling.
- `xlog_cil_push_now()` coordinates push sequence state and optionally flushes the push workqueue for synchronous callers to reduce later wait time.

## Concurrency and Locking

- `xc_ctx_lock` protects active context mutation vs. context switching. Transaction commits hold it read-locked; push work holds it write-locked.
- `xc_push_lock` protects `xc_push_seq`, `xc_push_commit_stable`, `xc_committing`, and push/commit/start wait queues.
- Per-CPU `xlog_cil_pcp` storage reduces contention for space counts, busy extents, and log item lists until push aggregation.
- CPU preemption is disabled around per-CPU insertion accounting with `get_cpu()` / `put_cpu()`.
- Lockless `waitqueue_active()` checks are only used when serialized by `xc_push_lock` or `xc_ctx_lock`, as documented in comments.

## Error Handling

- Ticket allocation for CIL checkpoints is no-fail because failing during checkpointing would make recovery difficult.
- Reservation overrun in `xlog_cil_insert_items()` dumps transaction details and forces log shutdown.
- Errors writing the checkpoint chain or commit record lead to shutdown/abort paths. If the commit iclog was not attached yet, the context is manually committed in abort mode so items are unpinned.
- CIL destroy asserts the active context is empty.

## Research Notes

The CIL is the performance and batching layer of XFS logging. Its design avoids reserving a separate checkpoint transaction up front; instead it safely transfers unused reservation from ordinary transactions into the checkpoint ticket. The implementation is heavily optimized for high-concurrency metadata workloads: per-CPU insertion, shadow buffers, bulk AIL insertion, sequence-ordered checkpoint pipelines, and bounded push workqueue concurrency all reduce contention while preserving recovery ordering.
