# File Research: sources/os/bsd/freebsd-src/sys/sys/runq.h

Read completely: 124 lines.

## Purpose
Declares kernel run queue structures and helper APIs used by scheduler implementations.

## Main Elements
- Kernel-only header; rejects non-kernel inclusion.
- Defines maximum priority, priorities per queue, number of queues, and priority-to-queue-index mapping.
- Defines status word type and bit/word helper macros for finding non-empty run queues.
- Defines `TAILQ_HEAD(rq_queue, thread)`, `struct rq_status`, and `struct runq`.
- Declares initialization, empty test, add by priority/index, remove, non-empty test, choose, choose-with-fuzz, range first-thread, and generic predicate-based queue search helpers.

## Dependencies And Integration
Used by scheduler implementations to manage runnable thread queues. Depends on thread `td_runq` linkage, `sys/queue.h`, priority values, and bit-scan helpers.

## Risk Notes
Run queue bitmaps must match queue contents. Scheduler locking must protect queue operations; stale status bits can lead to missed runnable threads or invalid selections.
