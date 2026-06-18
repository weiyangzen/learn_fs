# sources/user-network-fs/mergerfs/vendored/moodycamel/blockingconcurrentqueue.h

## Purpose
`blockingconcurrentqueue.h` wraps `moodycamel::ConcurrentQueue` with a semaphore so consumers can block until items are available.

## Important APIs, Types, and Functions
The template `moodycamel::BlockingConcurrentQueue<T, Traits>` exposes producer/consumer token types, queue constants from the underlying concurrent queue, constructors with capacity/producer sizing, move/swap support, `enqueue`, `try_enqueue`, bulk enqueue variants, `try_dequeue`, bulk try-dequeue variants, blocking `wait_dequeue`, timed wait variants, `size_approx`, `is_lock_free`, and non-member `swap`.

## Control Flow
Successful enqueue operations delegate to `inner` and then signal the `LightweightSemaphore` once or by bulk count. Dequeue operations first acquire one or more semaphore permits, then spin on `inner.try_dequeue` or `inner.try_dequeue_bulk` until the promised item count is retrieved. Blocking waits call `sema->wait` or `waitMany`; timed waits return false/zero if the semaphore times out. The semaphore is allocated using the queue traits allocator and held by a unique_ptr with custom deleter.

## State and Persistence
State is in-memory: the underlying lock-free queue plus semaphore permit count. Queue movement is supported only when no other thread is using it. Tokens remain tied to the moved queue state.

## Dependencies and Integration Points
It includes `concurrentqueue.h` and `lightweightsemaphore.h`, plus standard type traits, memory, chrono, and time headers. It is a vendored general-purpose concurrency primitive used by components that need MPMC queues with blocking consumers.

## Risks
Correctness depends on signaling the semaphore only after successful enqueue and consuming permits before dequeue. After a semaphore permit is acquired, dequeue spins until an item appears, relying on the underlying queue's eventual visibility. `size_approx` is only an estimate. Destruction or move while threads are active is unsafe.

## Test Signals
Test single/multiple producers and consumers, explicit tokens, bulk enqueue/dequeue counts, timed wait expiry, move/swap only while quiescent, allocation failure construction, semaphore count consistency under failed try_enqueue, and high-contention stress with sanitizers.
