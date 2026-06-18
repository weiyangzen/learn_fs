<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp

Purpose: `BoundedQueue<T,Traits>` wraps `moodycamel::BlockingConcurrentQueue` with a `LightweightSemaphore` so producers cannot exceed a configured queue depth. It is used by `ThreadPool` to apply backpressure to work submission.

Important APIs: producers can call blocking `enqueue`, nonblocking `try_enqueue`, timed `try_enqueue_for`, or `enqueue_unbounded` for control messages that must bypass the depth limit. Consumers use `wait_dequeue`, which signals a freed slot after removing an item. `make_ptoken` and `make_ctoken` expose moodycamel producer/consumer tokens.

Control flow and state: `_slots` starts at `max_depth`; enqueue waits or decrements before pushing into `_queue`, and successful dequeue increments slots. The queue object is not copyable or movable, preserving token and semaphore invariants.

Risks and test signals: ordinary enqueue calls ignore the return value from the underlying queue, so an allocation/enqueue failure after a slot wait could leak capacity. `enqueue_unbounded` intentionally violates the depth limit and can grow memory use if abused. Tests should stress full queues, timed enqueue expiry, token and non-token paths, consumer slot recovery, and shutdown/control-message scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp -->
