# sources/storage-engines/wiredtiger/src/support/mtx_rw.c

## Purpose
`mtx_rw.c` implements WiredTiger's ticket-based reader/writer lock. It provides shared and exclusive locking with fast paths, queued reader groups, writer ordering, condition-variable fallback, statistics accounting, and ThreadSanitizer synchronization annotations.

## Important APIs, Types, and Functions
The public internal APIs are `__wt_rwlock_init`, `__wt_rwlock_destroy`, `__wt_try_readlock`, `__wt_readlock`, `__wt_readunlock`, `__wt_try_writelock`, `__wt_writelock`, `__wt_writeunlock`, and `__wt_rwlock_islocked`. Static wait predicates `__read_blocked` and `__write_blocked` are used by condition waits. The `WT_RWLOCK` state packs `current`, `next`, `reader`, `readers_queued`, and `readers_active` into one atomically updated 64-bit value.

## Control Flow
Try-read succeeds only when no writer is active or queued for the current ticket and reader count will not overflow. Blocking read first tries the no-writer fast path; if a writer is active, readers queue behind existing writers by sharing `reader = next`, subject to a cap tied to active writers. Queued readers spin, yield, then wait until their ticket becomes current. Writers allocate a unique ticket by incrementing `next`, avoiding wrap into `current`, then wait until their ticket is current and active readers drain. Unlocking a writer advances `current` and, if the next ticket belongs to queued readers, promotes queued readers to active.

## State and Persistence Behavior
Lock state is entirely in memory in `WT_RWLOCK.u.v`, two condition variables, stats-offset fields, and temporary session fields `current_rwlock` and `current_rwticket` during waits. No persistent state is written. Statistics are accumulated in connection and session stats arrays when offsets are configured and stats are enabled.

## Dependencies and Integration Points
The implementation depends on WiredTiger atomic 64-bit CAS/load/store wrappers, condition variables, pause/yield/wait helpers, stat infrastructure, session flags, diagnostic yield hooks, and memory-barrier macros. It is a foundational synchronization primitive for shared WiredTiger subsystems that need read-mostly concurrency with exclusive updates.

## Risks
Correctness depends on reading and CASing the whole 64-bit lock word, because separate field reads can observe mixed batches. The ticket fields are one byte and wrap at 256, so writers must wait when allocation would catch `current`. Reader counts can overflow and must reject or stall new readers. The queued-reader cap is a throughput/fairness tradeoff; incorrect changes can starve writers or destabilize write-heavy workloads. Acquire/release barriers are required because ownership is not established merely by ticket allocation.

## Test Signals
Concurrency tests should cover many readers, writer exclusivity, reader-to-writer handoff, writer-to-reader-group handoff, try-lock failure behavior, ticket wrap pressure, reader count overflow handling, stats increments and wait-time accounting, condition-variable wakeups after spin/yield, and TSan builds. Stress tests should include write-heavy workloads to validate queued-reader limits and fairness.
