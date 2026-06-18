# sources/user-network-fs/smblibrary/Utilities/Generics/BlockingQueue.cs

Purpose: `BlockingQueue<T>` is a monitor-based producer/consumer queue with stop and abort semantics.

Important APIs/types/functions: `Enqueue(T)`, `Enqueue(List<T>)`, `TryDequeue(out T)`, `Stop()`, `Abort()`, and `Count`.

Control flow: enqueue ignores requests after stopping, locks the queue, enqueues items, increments `m_count`, and pulses a waiter when transitioning from empty. Dequeue waits while empty unless stopping, returns false when stopped and empty, otherwise dequeues and decrements. Abort clears queued items and stops.

State and persistence behavior: in-memory queue state only; `m_stopping` gates producers/consumers.

Dependencies and integration points: uses `Queue<T>` and `Monitor`; suitable for internal worker pipelines.

Risks: `Count` returns `m_count` without locking or `volatile`, so readers can see stale values. `Abort` clears `m_queue` but does not reset `m_count`, making `Count` inaccurate after abort. `Enqueue(List<T>)` only pulses one waiter even when many items arrive.

Test signals: multi-producer/multi-consumer tests, stop unblocks waiters, enqueue-after-stop behavior, abort count correctness, and count visibility under concurrency.
