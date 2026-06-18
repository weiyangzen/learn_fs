# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint.h

## Purpose

Defines the public internal checkpoint data structures and prototypes shared across WiredTiger checkpoint implementation files. It captures per-session checkpoint work state, connection-wide checkpoint server/stat state, checkpoint metadata records, snapshot metadata, cleanup thread state, and parallel page-reconciliation queues.

## Important APIs, Types, And Functions

`WT_CKPT_SESSION` tracks checkpoint cursor write generation, handle lists, crash-test points, named-checkpoint drop list, current checkpoint time, and size delta. `WT_CKPT_CONNECTION` holds handle stats, checkpoint server state, timer stats, reconciliation/sync accumulators, most recent checkpoint time, progress counters, and previous base write generation. `WT_CKPT_BLOCK_MODS` records incremental backup block-modification bitstrings. `WT_CKPT` is the central checkpoint descriptor with name, order, wall-clock time, size, write generations, block metadata/checkpoint cookies, backup block-mod entries, time aggregate, address/raw cookie buffers, next page ID, block-manager private state, and checkpoint flags.

`WT_CKPT_SNAPSHOT` preserves checkpoint ID, oldest/stable timestamps, write generation, transaction snapshot range/list/count. `WT_CHECKPOINT_CLEANUP` models the cleanup thread. `WT_CHECKPOINT_PAGE_TO_RECONCILE` is a parallel reconcile work item. `WT_CHECKPOINT_RECONCILE_THREADS` contains the thread group, work/done queues, synchronization primitives, and private snapshot buffer for checkpoint workers. Macros expose checkpoint iteration and parallel-checkpoint status/thread count. Prototypes export checkpoint lifecycle, server, parallel reconciliation, stats, snapshot, and ckpt-list helpers.

## Control Flow

The header itself has no executable control flow, but it defines the state passed through checkpoint phases: checkpoint setup populates `WT_CKPT_SESSION` and `WT_CKPT_CONNECTION`; metadata and btree/block layers exchange `WT_CKPT`; transaction code fills `WT_CKPT_SNAPSHOT`; sync/reconciliation queues use `WT_CHECKPOINT_PAGE_TO_RECONCILE`; cleanup and server code consume `WT_CHECKPOINT_CLEANUP` and `WTI_CKPT_THREAD`. Parallel checkpoint macros gate whether btree sync pushes page work to helper threads or uses the single-threaded path.

## State And Persistence Behavior

Several fields represent durable checkpoint metadata: names, order, checkpoint cookies, block metadata, block modification bitstrings, time aggregates, write generations, and snapshot timestamps. Other fields are transient runtime state: handle arrays, crash testing controls, cleanup thread handles, progress counters, private worker snapshots, and queue entries. `ckpt_size_delta` is explicitly accumulated during a checkpoint and applied to connection-level database size only after success.

## Dependencies And Integration Points

Includes `checkpoint_private.h` for private enums/stats/thread/timer types. The prototypes link this header to transaction checkpoint code, metadata, btree sync/reconciliation, block manager, checkpoint server, checkpoint cleanup, stats publishing, and unit tests. Many structures are also consumed by generated prototype machinery, so field/name changes cascade through internal checkpoint modules.

## Risks

These structures are cross-module contracts; changing flags, snapshot ownership, queue fields, or checkpoint metadata buffers can break metadata parsing, incremental backup, recovery, or parallel reconciliation. The `WT_CKPT_FOREACH` macro stops on `name == NULL`, while the private macro in `checkpoint_private.h` also considers `order`, so callers must choose the correct iterator for partially named checkpoints. Worker snapshot buffers must remain valid while helper threads run.

## Test Signals

Signals come from checkpoint/recovery tests, named checkpoint tests, incremental backup tests, timestamped checkpoint visibility tests, parallel checkpoint tests with `checkpoint_threads > 1`, crash-test configurations using checkpoint crash points, and unit tests behind `HAVE_UNITTEST` such as checkpoint-list skipping helpers. ABI-like internal consistency is also checked by generated prototype builds.
