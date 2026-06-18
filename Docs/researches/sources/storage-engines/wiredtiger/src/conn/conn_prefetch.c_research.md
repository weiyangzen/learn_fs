# sources/storage-engines/wiredtiger/src/conn/conn_prefetch.c

## Purpose
This file implements the connection prefetch queue and prefetch worker thread group. It lets traversal paths enqueue disk refs for asynchronous page reads while protecting refs and internal pages from eviction until workers finish.

## Important APIs, Types, and Functions
Public functions are `__wti_conn_prefetch_init`, `__wti_conn_prefetch_destroy`, `__wti_prefetch_create`, `__wt_conn_prefetch_queue_push`, `__wt_conn_prefetch_clear_tree`, and `__wti_prefetch_destroy`. Worker helpers are `__prefetch_thread_chk` and `__prefetch_thread_run`. Important types are `WT_CONN_PREFETCH`, `WT_PREFETCH_QUEUE_ENTRY`, `WT_THREAD_GROUP`, `WT_REF`, and `WT_BTREE`.

## Control Flow and Behavior
Initialization sets up the queue and spin lock. Create reads `prefetch.available`; if unavailable it does not start workers. If available, it sets `WT_CONN_SERVER_PREFETCH` and creates a fixed-size thread group. Workers wait on the group condition, pop queued entries under the prefetch lock, skip and clear entries under clean-cache pressure, increment the owning btree `prefetch_busy` counter, prefetch via `__wt_prefetch_page_in` under the saved dhandle, clear `WT_REF_FLAG_PREFETCH`, decrement busy, and ignore benign `WT_NOTFOUND`/`WT_RESTART`.

Queue push avoids adding work under clean-cache pressure or when tree eviction is disabled. It deduplicates by `WT_REF_FLAG_PREFETCH`, CAS-locks disk refs before queueing to prevent eviction/free races, sets the prefetch flag, restores ref state, appends the queue entry, increments the queue count, unlocks, and signals workers. Clear-tree removes queued entries for one dhandle or all dhandles, clears flags, decrements queue count, and for per-tree clearing waits until `prefetch_busy` drains.

## State and Persistence
State is volatile: the queue, lock, queue count, prefetch availability, server flag, thread group, and per-btree `prefetch_busy`. No data is persisted; prefetch is a performance feature.

## Dependencies and Integration Points
The file depends on eviction pressure checks, ref state transitions, dhandle lifetime, btree eviction-disable flags, thread groups, timing stress hooks, TSAN-suppressed counters, and statistics. It is started from connection workers and stopped before data handles and eviction are destroyed.

## Risks
The critical risks are ref lifetime races, missing flag cleanup on skipped/error paths, queue entries referencing closing dhandles, cache pressure causing prefetch to worsen eviction, and deadlock if per-tree close waits while workers cannot drain. The code uses ref CAS, prefetch flags, `prefetch_busy`, and queue clearing to mitigate those hazards.

## Test Signals
Signals include prefetch statistics for skipped conditions, queue count returning to zero after clear/destroy, eviction/verify corruption paths that stop prefetch safely, stress timing flags, and tests that close trees while prefetch workers are active.
