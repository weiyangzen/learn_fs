# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmthread.c

## Purpose

Implements the regular OCFS2 DLM maintenance thread. This thread processes dirty lock resources, grants blocked/converting locks when compatible, queues and flushes AST/BAST callbacks, and purges unused lock resources.

## Major Responsibilities

- Determine whether lock resources are unused and purgeable.
- Maintain the purge list.
- Drop remote references before purging secondary lock resources.
- Shuffle lock queues when lock compatibility changes.
- Queue ASTs and BASTs for local or remote delivery.
- Run a kthread that repeatedly processes dirty lock resources and pending callbacks.

## Important Entry Points

- `dlm_launch_thread()` starts the per-domain DLM kthread.
- `dlm_complete_thread()` stops it.
- `dlm_kick_thread()` marks an optional lock resource dirty and wakes the thread.
- `__dlm_dirty_lockres()` adds a master-owned lock resource to the dirty list.
- `dlm_lockres_calc_usage()` recalculates purge-list membership.
- `__dlm_do_purge_lockres()` performs locked purge for already validated unused resources.

## Lock Resource Usage And Purge

`__dlm_lockres_has_locks()` checks whether granted/converting/blocked queues are empty.

`__dlm_lockres_unused()` requires all of the following:

- no locks on any queue
- no inflight locks
- not dirty and not on dirty list
- not recovering or waiting for recovery
- no refmap bits for remote references

`__dlm_lockres_calc_usage()` adds unused resources to `dlm->purge_list` with a timestamp and removes resources that become used again.

`dlm_run_purge_list()` processes purge candidates after `DLM_PURGE_INTERVAL_MS`, or immediately during shutdown. It avoids purging resources that became used, are migrating, or have inflight assert-master workers.

## Purge Operation

`dlm_purge_lockres()` handles master and non-master cases.

For non-master resources:

- Sets `DLM_LOCK_RES_DROPPING_REF`.
- Waits for `DLM_LOCK_RES_SETREF_INPROG` to clear.
- Sends `dlm_drop_lockres_ref()` to clear this node’s bit from the master refmap.
- Handles in-progress deref responses.

For master resources:

- Verifies the resource is unused.
- Unhashes it.
- Removes it from tracking.
- Clears dropping-ref state and wakes waiters when appropriate.

`__dlm_do_purge_lockres()` is a lower-level variant used by recovery cleanup paths when locks are already held.

## Dirty Lock Resource Processing

`__dlm_dirty_lockres()` adds master-owned lock resources to `dlm->dirty_list` unless migration or dirty blocking state prevents it. Dirty resources get a reference while queued.

`dlm_thread()` pulls dirty resources from the list. For each resource:

- Confirms it is still master-owned.
- Defers processing if in progress, recovering, or recovery-waiting.
- Calls `dlm_shuffle_lists()` when safe.
- Clears dirty state.
- Recalculates purge usage.
- Requeues deferred resources.

The thread throttles after `DLM_THREAD_MAX_DIRTY` resources to avoid long scheduling latency.

## Queue Shuffling

`dlm_shuffle_lists()` is the core grant engine for local-master lock resources.

For converting locks:

- Looks at the first converting lock.
- Checks compatibility against granted and other converting locks.
- Queues BASTs against incompatible locks.
- If compatible, changes the lock type to requested convert type, moves it to granted, sets `DLM_NORMAL`, and queues an AST.

For blocked locks:

- Looks at the first blocked lock.
- Checks compatibility against granted and converting locks.
- Queues BASTs for incompatible holders.
- If compatible, moves it to granted, sets `DLM_NORMAL`, and queues an AST.

The function loops back to converting after each grant so conversions retain priority over blocked new grants.

## AST/BAST Delivery

`dlm_flush_asts()` drains:

- `dlm->pending_asts`
- `dlm->pending_basts`

For ASTs:

- Takes an extra lock reference.
- Removes the AST list reference.
- Sends remote AST or invokes local AST.
- Clears `ast_pending` unless another AST was queued while flushing.
- Releases the lock resource’s AST reservation.

For BASTs:

- Reads and resets `highest_blocked`.
- Removes the BAST list reference.
- Sends proxy BAST or invokes local BAST.
- Clears `bast_pending` unless requeued.
- Releases AST reservation.

Finally, it wakes `dlm->ast_wq`.

## Concurrency

- `dlm->spinlock` protects dirty and purge lists.
- `res->spinlock` protects lock-resource state and queues.
- `dlm->ast_lock` protects pending AST/BAST lists and AST reservations.
- Wait queues are used for thread wakeups and AST flushing completion.
- The code deliberately drops the global DLM lock before queue shuffling and callback delivery.

## Dependencies

- Lock compatibility and AST queue helpers from DLM common code.
- Remote AST/BAST message send helpers.
- Lock resource hash/tracking helpers.
- Linux kthreads, wait queues, lists, spinlocks, and scheduling primitives.

## Research Notes

This file is the local scheduling engine for a DLM master. Recovery and network handlers mark resources dirty; this thread later reconciles queues and issues callbacks. It is tightly coupled with recovery because recovering/migrating resources are explicitly deferred and purging is blocked until recovery state clears.
