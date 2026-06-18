<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/PriorityMultiLock.h -->
# sources/storage-engines/foundationdb/flow/include/flow/PriorityMultiLock.h

Purpose: This header implements a weighted, priority-aware multi-user lock for Flow actors. It grants up to a configured total concurrency while distributing running slots among priority classes according to weights and pending demand.

Important APIs and types: Public API includes `PriorityMultiLock(int concurrency, std::string weights)`, `PriorityMultiLock(int, std::vector<int>)`, `Future<Lock> lock(int priority)`, `halt`, `kill`, `toString`, `maxPriority`, and runner/waiter count accessors. `Lock` wraps a `Promise<Void>`; releasing or destroying all copies of the lock's promise future releases the slot.

Control flow: `lock()` either grants immediately when slots are available and the priority is below its current weighted capacity, or enqueues a `Waiter` in the priority queue and puts that priority in an intrusive waiting list. The runner actor wakes on releases and repeatedly selects the next waiting priority with capacity. `handleRelease` tracks the holder future; immediate releases are handled inline, otherwise a callback invokes `releaseRunner`.

State and persistence behavior: State is in-memory: total concurrency, available slots, total waiter count, pending weights, per-priority queues, runner counts, waiting priority list, and killed/halted flags. There is no persistence. `halt` stops new grants without erroring existing waiters; `kill` also clears queues and makes new lock attempts throw `broken_promise`.

Dependencies and integration points: It depends on Flow futures/promises, `AsyncTrigger`, `Deque`, `ReferenceCounted`, and Boost intrusive lists. It is suitable for throttling actor work where classes need weighted fairness rather than strict numeric priority ordering.

Risks: The scheduler assumes priority ids are valid indexes and weights are meaningful positive values; invalid priorities or zero total weights can assert or divide badly. Cancellation/release behavior depends on lock promise lifetime, so accidental copies can hold slots longer than expected. `halt` leaves waiters unresolved by design. Intrusive list membership must remain consistent when queues empty.

Test signals: Tests should cover immediate grants, weighted distribution across priorities, FIFO behavior within a priority, release by explicit `release()` and scope destruction, cancellation of waiters, `halt` versus `kill`, count accessors, and stress tests that ensure no waiting priority is stranded.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/PriorityMultiLock.h -->
