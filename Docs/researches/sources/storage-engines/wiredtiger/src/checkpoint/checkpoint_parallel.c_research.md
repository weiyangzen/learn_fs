# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_parallel.c

## Purpose

Implements helper-thread infrastructure for parallel page reconciliation during checkpoints. When `checkpoint_threads` is greater than one, btree sync can push dirty page refs to a worker queue while the main checkpoint thread later drains results, releases page references, and commits/releases worker transactions in checkpoint phase order.

## Important APIs, Types, And Functions

Public functions are `__wt_checkpoint_parallel_thread_create`, `__wt_checkpoint_parallel_thread_destroy`, `__wt_checkpoint_parallel_push_work`, `__wt_checkpoint_parallel_finish`, `__wti_checkpoint_parallel_release_snapshot`, and `__wti_checkpoint_parallel_commit`. Internal queue/thread helpers include `__checkpoint_parallel_pop_work`, `__checkpoint_parallel_push_done`, `__checkpoint_parallel_pop_done`, queue-empty checks, `__checkpoint_parallel_thread_run`, `__checkpoint_parallel_thread_stop`, `__checkpoint_parallel_thread_release_snapshot`, and `__checkpoint_parallel_thread_commit`.

The core types are `WT_CHECKPOINT_RECONCILE_THREADS` and `WT_CHECKPOINT_PAGE_TO_RECONCILE`, with a `WT_THREAD_GROUP`, work/done TAILQs, spin locks, condition variable, done semaphore, work counter, and a private checkpoint transaction snapshot shared by all worker sessions.

## Control Flow

Thread creation stores the connection's reconcile-thread structure, reads `checkpoint_threads`, disables parallel mode for one thread, otherwise sets the server flag, initializes queues/locks/condition/semaphore, and creates a fixed-size thread group. Pushing work allocates an entry containing the current data handle, isolation level, checkpoint snapshot pointer, page ref, reconcile flags, and release flags, then queues it under `work_lock`, increments `work_pushed`, and signals workers.

Each worker marks its session as checkpoint/checkpoint-worker, waits for work, loops over available entries, begins a transaction if needed, imports the private checkpoint snapshot, restores isolation, reconciles the page under the entry's data handle, records elapsed reconciliation ticks, increments success stats, stores the result, and posts the entry to the done queue. On error it logs and stops processing.

Finish loads the number of pushed work items, waits on the done semaphore until all are popped, accumulates result and page-release errors with `WT_TRET`, releases each page ref using the stored flags, sums reconcile time, frees entries, asserts both queues are empty, and resets `work_pushed`. Snapshot release and commit functions run callbacks across the thread group after all work is empty. Destroy clears the server flag, signals workers, finishes outstanding done entries, destroys the thread group and synchronization primitives, and frees the private snapshot buffer.

## State And Persistence Behavior

The file manages transient checkpoint worker state. Persistent effects occur through `__wt_reconcile`, which writes checkpoint page images and block state. Worker transactions and imported snapshots ensure all parallel page reconciliations see the same checkpoint-consistent transaction view as the main checkpoint. The main thread remains responsible for committing or rolling back worker transactions and releasing snapshots in the correct checkpoint phase.

## Dependencies And Integration Points

Integrated with btree sync (`bt_sync.c`) for pushing work and collecting reconciliation time, transaction snapshot import/release/commit, data-handle switching via `WT_WITH_DHANDLE`, page release semantics, thread group infrastructure, semaphores, condition variables, checkpoint stats, and checkpoint macros from `checkpoint.h`. It also depends on the checkpoint prepare path having populated `checkpoint_snapshot`.

## Risks

The work counter must match queued entries; otherwise finish can wait forever or assert queue corruption. Page references must be released exactly once by the main thread after worker reconciliation. Worker transactions must not survive thread-group stop, enforced by assertions and panic. Snapshot buffers must remain valid until all worker sessions have released snapshots. Error propagation is intentionally aggregated, but destroy suppresses finish errors after warning, so shutdown paths can hide prior reconcile failures. Queue-empty assertions catch phase-order violations when release/commit is called before all work is done.

## Test Signals

High-signal tests set `checkpoint_threads > 1` and generate many dirty pages across handles, then verify successful checkpoints, reopened data, and `checkpoint_parallel_pages_reconciled` increments. Fault-injection tests should force reconcile errors and page-release errors, verify finish returns errors, and ensure destroy still frees resources. Race tests should exercise shutdown/reconfigure with workers waiting, and phase assertions should be covered by diagnostics builds.
