# File Research: sources/os/linux/linux/io_uring/io-wq.c

## Purpose
Implements io_uring’s internal worker-thread pool for asynchronous work that cannot complete inline.

## Main Structures
- `struct io_worker`: one worker thread, including refcount, flags, task, workqueue/account pointers, current work, creation state, and RCU/delayed-work storage.
- `struct io_wq_acct`: bounded or unbounded worker accounting, worker lists, pending work list, and running count.
- `struct io_wq`: per-task workqueue with shared hash serialization state, worker refs/completions, CPU hotplug node, owner task, bounded/unbounded accounts, wait entry, hash tails, and CPU mask.
- `struct io_cb_cancel_data`: cancellation match callback state.

## Main Functional Areas
- Worker lifecycle:
  - `create_io_worker()`, `create_worker_cb()`, `create_worker_cont()`
  - `io_wq_worker()`
  - `io_worker_exit()`
  - `io_wq_exit_start()`, `io_wq_exit_workers()`, `io_wq_put_and_exit()`
- Scheduling and execution:
  - `io_wq_enqueue()`
  - `io_worker_handle_work()`
  - `io_get_next_work()`
  - `io_wq_hash_work()`
  - `io_wq_inc_running()` / `io_wq_dec_running()`
- Cancellation:
  - `io_wq_cancel_cb()`
  - `io_wq_cancel_pending_work()`
  - `io_wq_cancel_running_work()`
  - `io_run_cancel()`
- Worker creation/retry:
  - task_work-based creation on the owner task.
  - delayed retry for transient `create_io_thread()` failures.
- CPU/limit management:
  - CPU hotplug callbacks update worker affinity masks.
  - `io_wq_cpu_affinity()` changes allowed CPUs.
  - `io_wq_max_workers()` gets/sets bounded and unbounded worker limits.
- Idle behavior:
  - idle workers enter free list and exit after timeout or when `EXIT_ON_IDLE` is set.

## Important Design Points
- Work is split into bounded and unbounded accounts. Unbounded max workers are capped by `RLIMIT_NPROC`.
- Hashed work items sharing a hash key do not run concurrently; hash tails let the queue skip runs of identical hashes.
- Current work is set before execution so cancellation can find work removed from pending queues.
- Worker creation is often queued as task_work on the original task to keep worker creation associated with the owning task.
- `IO_WQ_BIT_EXIT` causes new work to be canceled and workers to drain/exit.
- Worker sleep/running hooks are called from scheduler integration to maintain running counts and spawn replacement workers when needed.
- Exit waits are tuned to avoid hung-task false positives under heavy long-running io-wq load.

## Cross-File Relationships
- Public API and flags are in `io-wq.h`.
- Core io_uring submits async work to io-wq and receives completed work through `io_wq_submit_work()` / `io_wq_free_work()` implemented elsewhere.
- Cancellation in `cancel.c` calls `io_wq_cancel_cb()` and `io_wq_exit_start()`.
- Eventfd code uses `io_wq_current_is_worker()` for async eventfd behavior.

## Risks / Review Notes
- Worker, account, and hash locking is complex: raw spinlocks, RCU worker lists, waitqueue hash serialization, task_work, and completions all interact.
- Hashed work correctness depends on maintaining `hash_tail[]` when inserting/removing pending work.
- Cancellation can return “pending canceled” or “running cancellation attempted”; callers must interpret `IO_WQ_CANCEL_*` correctly.
- Worker creation failure paths cancel pending work if no workers remain.
