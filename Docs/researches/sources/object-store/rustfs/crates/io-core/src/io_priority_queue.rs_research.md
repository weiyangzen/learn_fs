# sources/object-store/rustfs/crates/io-core/src/io_priority_queue.rs

Purpose: three-lane I/O request queue with high, normal, and low priorities plus simple starvation prevention.

Important APIs/types: `IoRequest` records id, `IoPriority`, size, queued time, and sequential flag. `IoQueueStatus` reports count, total size, oldest wait, and processed count. `IoPriorityQueue` provides `enqueue`, `dequeue`, `status`, `total_status`, `peek`, `clear`, and config access.

Control flow: `enqueue` increments `next_id`, creates a request, and pushes it to the matching `VecDeque` only if that queue is below capacity. `dequeue` prefers high, then normal, then low unless lower-priority queues are starved based on `last_dequeue` and `starvation_threshold`. Successful dequeue updates `last_dequeue` and processed stats for that priority. Status methods aggregate current queue contents and processed counters.

State and persistence: in-memory queues, ID counter, last-dequeue timestamps, and stats. No persistence or synchronization; callers must wrap it if used across threads.

Dependencies and integration: consumes `IoPriority` from `scheduler` and `IoPriorityQueueConfig` from `config`; re-exported through `lib.rs`.

Risks: `enqueue` returns an ID even if the queue is full and the request was dropped, so callers cannot distinguish accepted vs rejected requests. Starvation detection only starts after a priority has been dequeued once; a never-served low queue can fail to look starved. `total_status.oldest_wait` checks high before normal before low rather than the true oldest across queues. `peek` ignores starvation rules and always returns high before normal before low.

Test signals: tests cover priority order, status aggregation, capacity drop effect, clear, and peek non-removal.
