# sources/storage-engines/wiredtiger/src/tiered/tiered_work.c Research

## Purpose
This file implements the in-memory tiered-storage work queue. It creates, enqueues, dequeues, requeues, waits for, and frees `WT_TIERED_WORK_UNIT` entries for flush, flush-finish, local-remove, and shared-remove actions.

## Important APIs, Types, and Functions
- `__wt_tiered_work_free` releases the referenced tiered dhandle, updates flush-state accounting, signals flush waiters when all flush work is done, and frees the entry.
- `__wt_tiered_remove_work` removes all queued work for a tiered handle.
- `__wt_tiered_requeue_work` pushes an existing work item back without taking a new dhandle reference.
- Getter APIs `__wt_tiered_get_flush_finish`, `__wt_tiered_get_flush`, `__wt_tiered_get_remove_local`, and `__wti_tiered_get_remove_shared` pop matching work.
- Put APIs `__wt_tiered_put_flush_finish`, `__wt_tiered_put_remove_local`, `__wti_tiered_put_remove_shared`, and `__wti_tiered_put_flush` allocate and enqueue new work.
- `__wt_tiered_flush_work_wait` polls for queued flush work up to a caller-provided timeout.

## Control Flow and State
New work is allocated by a put function, initialized with type, object id, tiered pointer, and optional `op_val`, then passed to `__tiered_push_new_work`, which increments the tiered data-handle in-use count. Internal push takes `conn->tiered.tiered_lock`, appends to `conn->tiered.tieredqh`, increments creation statistics, releases the lock, adjusts atomic `flush_state` for flush work, and signals the tiered worker condition. Pop first does an unsafe empty peek to avoid unnecessary locking, then scans the queue under lock for a matching type and optional maximum `op_val`.

## State and Persistence Behavior
The queue itself is in-memory and not durable. Durability recovery is handled by `tiered_handle.c`, which scans metadata/local files and requeues needed work after restart. `op_val` is used either as a checkpoint generation bound for flush or as an expiration time for local-remove work. Dhandle acquisition keeps tiered handles from being swept while queued work references them.

## Dependencies and Integration Points
The queue depends on connection tiered state, spin locks, condition variables, queue macros, dhandle reference macros, atomic flush-state counters, statistics, and retention settings in `WT_BUCKET_STORAGE`. Tiered worker threads consume entries through the getter functions and must free or requeue entries.

## Risks and Edge Cases
Flush-state accounting must stay balanced across enqueue, requeue, and free; double-free or requeue misuse could cause waiters to think flushes are done too early or never done. `__wt_tiered_flush_work_wait` only detects queued flush entries, not necessarily in-flight ones, so correctness depends on `flush_state` and worker protocols elsewhere. The unsafe queue-empty peek intentionally suppresses TSan noise; real concurrency protection occurs in the locked scan. Remove-local scheduling uses wall-clock seconds plus retention, so clock changes can affect timing.

## Test Signals
Tests should cover enqueue/dequeue by each type, generation-filtered flush pops, retention-filtered local-remove pops, requeue without extra dhandle acquire, removing all work for a handle, flush-state increment/decrement and waiter signaling, timeout behavior in flush wait, and concurrent producer/consumer stress under TSan.
