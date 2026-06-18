# File Research: sources/os/linux/linux/io_uring/tw.c

io_uring task_work routing and local deferred-taskrun implementation. This file runs queued completions and retries in task context, moves abandoned work to fallback work, and wakes waiters for local work.

Key responsibilities:
- Executes fallback task_work from delayed work when normal task_work cannot be queued or task exits.
- Runs per-task task_work lists grouped by ring ctx with ctx locking and completion flushing.
- Implements local work queues for `IORING_SETUP_DEFER_TASKRUN`.
- Wakes submitter tasks based on pending local work and CQ wait thresholds.
- Moves local/retry work to fallback during teardown.
- Runs local work under lock with max/min event bounds and retry-list preservation.

Important data flows:
- `io_handle_tw_list()` walks an llist of requests, switches ctx locks as needed, invokes request task_work functions, flushes completions per ctx, and yields when rescheduling is needed.
- `io_req_local_work_add()` atomically pushes work to `ctx->work_llist`, marks taskrun, signals eventfd on first item, and wakes the submitter if wait thresholds are met.
- `__io_run_local_work()` drains retry work first, then reverses and runs new local work, preserving unprocessed nodes for later runs.
- Fallback work drains `ctx->fallback_llist` under `ctx->uring_lock`.

Concurrency and locking:
- Normal task_work uses the task’s `tctx->task_list` llist.
- Local deferred taskrun uses ctx-local lockless lists plus `ctx->uring_lock` while executing.
- `io_ctx_mark_taskrun()` uses RCU because ring resize can replace `ctx->rings`.

Important invariants:
- Linked requests disable lazy wake because the full link chain behavior is not known.
- Local task_work may only be run by the submitter task for deferred-taskrun rings.
- `ctx_flush_and_put()` must flush completions and drop refs whenever ctx changes.
