# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/putnext.c

## Purpose

`putnext.c` implements the C versions of STREAMS `putnext()` and `put()`. These functions deliver messages to downstream queue put procedures while respecting syncq/perimeter concurrency, queued message ordering, fast put locks, writer exclusion, and stack-depth protection.

Read completely: 679 lines.

## Main Responsibilities

- Delivers STREAMS messages to the next queue's put procedure (`putnext()`) or a specific queue's put procedure (`put()`).
- Uses syncq state to decide between direct putproc invocation, queue fill-and-drain, or deferred background processing.
- Implements fastlock/fastput handling for concurrent inner perimeters.
- Preserves message ordering when a queue already has syncq messages.
- Switches deep recursive put chains to background tail processing when kernel stack is near a redzone.
- Handles syncq claims, exclusive state, queued events, tail processing, and wakeups after putproc returns.
- Provides tracing hooks for STREAMS flow tracing.

## Important Data Structures And Globals

- `put_stack_notenough`: counter of stack-redirection events.
- `put_stack_needed`: tunable threshold for remaining stack space.
- `UseFastlocks`: controls fastlock use in `put()`; `putnext()` uses stream fastlock state when available.
- `queue_t`, `syncq_t`, `mblk_t`, `qinit`: STREAMS queue, synchronization queue, message, and put procedure structures.
- `sd_ciputctrl` and `sq_ciputctrl`: per-CPU fast concurrent-put control arrays.

## Control Flow And Algorithms

`putnext()` starts with the current queue, locks stream-head state, advances to `q_next`, and obtains the target syncq. If per-CPU fast concurrent-put state is available and the fastput bit remains set without stayaway/exclusive/event state, it increments the per-CPU put count and calls the put procedure without taking the normal syncq lock.

The slow path takes `SQLOCK`, claims the syncq with `sq_count`, and checks whether writers, exclusive users, pending events, exclusive waiters, or low stack space require queueing. In that case it drops `SQLOCK`, calls `qfill_syncq()`, and returns. Otherwise it marks non-concurrent perimeters exclusive before dropping `SQLOCK`.

After acquiring a valid claim/exclusive or concurrent permission, it calls the target putproc directly when no messages are queued. If syncq messages are already queued, it takes `QLOCK`; if the queue is empty it still calls putproc directly, otherwise it appends the message with `SQPUT_MP()` and drains with `qdrain_syncq()` to preserve FIFO ordering.

On return, it decrements either per-CPU fastput count or `sq_count`, handles `SQ_TAIL` or exclusive waiters through `putnext_tail()`, clears `SQ_EXCL` when this caller owns it, and exits.

`put()` mirrors the same algorithm but targets the supplied queue directly and only uses fastlocks when `UseFastlocks` is enabled.

## Dependencies And Integration

- Part of the STREAMS message delivery subsystem.
- Uses syncq helpers `qfill_syncq()`, `qdrain_syncq()`, and `putnext_tail()`.
- Integrates with STREAMS tracing and fault-injection/tracing macros.
- Relies on architecture frame-pointer/stack macros for stack-depth detection.

## Locking And Concurrency

The code coordinates `sd_lock` or per-stream CIPUT control locks, syncq locks, per-CPU CIPUT locks, and queue locks. It carefully makes syncq claims before dropping locks so queues/syncqs cannot close underneath processing. For fastput, per-CPU put counts let writer waiters stop new fast puts by clearing the fastput bit and then wait for counts to drain.

## Notable Risks And Invariants

- `mblk_t` input must not already be linked (`b_next`/`b_prev` are NULL) and must have a live data block.
- Queue/syncq pointers must not be referenced after `qfill_syncq()` because the queue may close.
- Stack redirection is essential for long module chains because `putnext()` can recurse through many STREAMS modules.
- Message ordering requires enqueue-and-drain when prior syncq messages exist.
- Lock ordering between `SQLOCK` and per-CPU CIPUT locks is handled carefully with tryenter fallback to avoid deadlock.

## Research Relevance

STREAMS is used by illumos networking, terminal, and some device/file-descriptor paths. This file is relevant to filesystem-adjacent event and I/O research because it defines how STREAMS messages are delivered safely under high concurrency and deep module stacks.
