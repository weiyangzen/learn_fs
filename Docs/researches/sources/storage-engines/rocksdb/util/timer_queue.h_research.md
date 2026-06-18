# sources/storage-engines/rocksdb/util/timer_queue.h

## Purpose

Defines a portable timer queue that runs handlers once at a future time or repeatedly when handlers request rescheduling.

## APIs, control flow, and state

Construction starts a worker thread. `add` assigns an id, computes an end time from `steady_clock`, stores the period and handler in a priority queue, and wakes the worker. `cancel` finds a matching pending item, moves its handler into an immediate id-zero work item so it still executes with `aborted=true`, and clears the original. `cancelAll` marks all live items id-zero at immediate time and sets `m_cancel`. `run` waits until the next due timer or until work changes, then `checkWork` executes due handlers outside the mutex and reschedules when requested and not globally cancelled. `shutdown` is not thread-safe, cancels all, enqueues a zero-delay finish handler, joins, and marks closed.

## Dependencies and integration

It uses `std::chrono`, condition variables, `port::Thread`, and sync points. It is self-contained and not namespace-wrapped until used from RocksDB tests.

## Risks and test signals

Handlers are guaranteed to run in the worker thread even when cancelled. The queue inherits from `priority_queue` to mutate the backing container during cancellation, so heap integrity relies on setting cancelled items to the earliest time. `timer_queue_test.cc` is mostly a smoke test and does not assert cancellation or repeat timing.
