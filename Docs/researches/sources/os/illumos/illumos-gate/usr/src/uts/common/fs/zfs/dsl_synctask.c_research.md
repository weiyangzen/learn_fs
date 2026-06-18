# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_synctask.c

## Role

Provides the DSL sync task framework: a way for open-context callers to schedule checked mutations to run later in txg syncing context under the DSL pool config lock.

## Main Flow

`dsl_sync_task_common()`:

1. Opens the pool.
2. Creates and assigns a DMU tx.
3. Builds a stack `dsl_sync_task_t`.
4. Runs the check function in open context under config read lock.
5. Queues the task on either `dp_sync_tasks` or `dp_early_sync_tasks`.
6. Commits the tx.
7. Waits for the txg to sync.
8. Retries on `EAGAIN` after waiting past deferred txgs.
9. Returns the sync-context task error.

`dsl_sync_task()`, `dsl_early_sync_task()`, and `dsl_sync_task_sig()` are public wrappers.

## Early Sync Tasks

Early sync tasks run before dirty dataset blocks are written in `dsl_pool_sync()`. The file documents that they can affect the current txg’s dirty data writeout and must not dirty metaslabs.

## No-Wait Tasks

`dsl_sync_task_nowait()` and `dsl_early_sync_task_nowait()` allocate a heap task, mark `dst_nowaiter`, and enqueue without a waiter. `dsl_sync_task_sync()` frees these after execution or space-check failure.

## Sync-Context Execution

`dsl_sync_task_sync()` performs:

- optional space check against `dsl_pool_unreserved_space()`,
- MOS triple-ditto estimate by multiplying requested task space by 3,
- config writer lock acquisition,
- check function rerun in sync context,
- sync function invocation only on check success.

## Important Contract

Check functions must be valid in both open and syncing context, or detect syncing context with `dmu_tx_is_syncing(tx)`. The framework guarantees config lock read mode for preliminary checks and writer mode for sync checks/mutations.
