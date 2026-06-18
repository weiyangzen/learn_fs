# sources/object-store/rustfs/crates/protocols/src/swift/expiration_worker.rs

## Purpose
`expiration_worker.rs` sketches a background cleanup worker for objects with `X-Delete-At` metadata. It maintains an in-memory priority queue ordered by expiration time and periodically processes expired entries.

## Important APIs, Types, And Functions
`ExpirationWorkerConfig` controls scan interval, batch size, distributed worker count, and worker id. `ExpirationMetrics` records scanned/deleted counts, iterations, duration, queue size, and errors. `ExpirationWorker` owns config, `BinaryHeap<Reverse<ExpirationEntry>>`, metrics, and a running flag behind async locks. Public methods include `new`, `start`, `stop`, `get_metrics`, `track_object`, `untrack_object`, and `scan_all_objects`. Internal helpers implement worker assignment hashing, cleanup iterations, and placeholder deletion.

## Control Flow
`start` sets `running`, logs startup, and spawns a Tokio loop that ticks every configured interval. Each cleanup iteration peeks expired entries from the heap up to batch size, parses `account/container/object`, calls `delete_expired_object`, updates metrics, and logs summary. `track_object` hashes the path for distributed ownership before pushing into the heap. `untrack_object` only logs because arbitrary heap removal is not implemented.

## State, Persistence, And Dependencies
The queue and metrics are process-local only; they are lost on restart. Distributed assignment is deterministic per process but not coordinated through shared storage. Dependencies are Tokio locks/tasks/timers, a binary heap, tracing, and Swift result types.

## Integration Points
The worker is exported by `mod.rs`, but search within the Swift folder shows no call from `object::put_object` to `track_object` and no service startup call. `scan_all_objects` and `delete_expired_object` contain TODOs rather than object-store integration.

## Risks And Test Signals
This is not yet an enforcing expiration service: expired objects are never really deleted, startup recovery is unimplemented, and queued entries are not durable. `untrack_object` does not remove heap entries, so stale entries rely on deletion-time verification that is also placeholder. The distributed test asserts exactly one of workers 0 and 1 handles a path when max_workers is 4, which is not generally guaranteed because assignment could be worker 2 or 3 for other paths. Tests cover heap ordering, hashing determinism, lifecycle flags, and tracking metrics, but not real deletion or recovery.
