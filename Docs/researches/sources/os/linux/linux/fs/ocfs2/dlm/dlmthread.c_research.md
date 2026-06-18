# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmthread.c

## Purpose
Implements the main OCFS2 DLM maintenance thread. It purges unused lock resources, shuffles converting/blocked queues on mastered resources, and flushes pending AST/BAST callbacks.

## Major Responsibilities
- Provides lockres wait and usage helpers:
  - `__dlm_wait_on_lockres_flags()`
  - `__dlm_lockres_has_locks()`
  - `__dlm_lockres_unused()`
  - `__dlm_lockres_calc_usage()`
  - `dlm_lockres_calc_usage()`
- Manages purge-list lifecycle for unused lock resources.
- Drops remote mastery refs before purging non-master resources.
- Runs queue grant logic in `dlm_shuffle_lists()`.
- Marks lock resources dirty through `dlm_kick_thread()` and `__dlm_dirty_lockres()`.
- Starts/stops the DLM thread with `dlm_launch_thread()` and `dlm_complete_thread()`.
- Flushes AST and BAST callback queues in `dlm_flush_asts()`.

## Key Thread Flow
- `dlm_thread()` loops until stopped.
- Each pass:
  1. Runs `dlm_run_purge_list()`, forcing purge during shutdown.
  2. Pulls up to `DLM_THREAD_MAX_DIRTY` resources from `dirty_list`.
  3. Skips or requeues resources that are in progress, recovering, migration-waiting, or otherwise unsafe to shuffle.
  4. Calls `dlm_shuffle_lists()` on stable local-master resources.
  5. Recalculates purge eligibility.
  6. Flushes pending ASTs and BASTs.
  7. Sleeps on `dlm_thread_wq` unless more dirty work remains.

## Queue Shuffling Semantics
- Converting queue is processed before blocked queue.
- A converting lock can be granted if compatible with all granted and other converting locks.
- Incompatible holders receive BASTs and get `highest_blocked` updated.
- Granted conversions and blocked lock grants are moved to the granted list, set `lksb->status = DLM_NORMAL`, and get ASTs queued.
- The code assumes it holds `ast_lock` and `res->spinlock`, and asserts the resource is not migrating/recovering/in-progress.

## Purging Semantics
- A lockres is unused only if it has no granted/converting/blocked locks, no inflight locks, no dirty state/list membership, no recovery state, and no refmap bits.
- Purge list entries hold a lockres ref.
- Non-master purge first marks `DLM_LOCK_RES_DROPPING_REF`, waits for setref completion, and sends a deref to the master.
- After successful purge, the resource is unhashed and removed from tracking.

## Concurrency and Synchronization
- `dlm->spinlock` protects global lists and purge counters.
- `res->spinlock` protects per-resource queues/state.
- `dlm->ast_lock` protects pending AST/BAST lists and callback pending flags.
- Wait queues used: `res->wq`, `dlm_thread_wq`, and `ast_wq`.
- Refcounts are deliberately taken while resources/locks are temporarily removed from lists or callbacks are in progress.

## Risks and Invariants
- Non-local resources on the dirty list are considered a fatal invariant violation.
- Purging an in-use resource triggers diagnostics and `BUG()`.
- Dirty resources in recovery or in-progress states are requeued rather than shuffled.
- AST/BAST flushing handles callbacks that are requeued while a previous callback is being delivered.
