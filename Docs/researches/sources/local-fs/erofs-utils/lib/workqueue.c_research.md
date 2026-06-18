# File Research: sources/local-fs/erofs-utils/lib/workqueue.c

## Scope

This file implements a simple bounded pthread workqueue used by multi-threaded erofs-utils paths.

## Public And Internal APIs Covered

- `erofs_alloc_workqueue()` initializes and starts worker threads.
- `erofs_queue_work()` enqueues one `struct erofs_work`.
- `erofs_destroy_workqueue()` shuts down workers and destroys queue resources.
- Internal `worker_thread()` drains queued work and invokes optional per-thread start/exit hooks.

## Control Flow And Behavior

- Workers call `on_start`, then loop waiting on `cond_empty` while there are no jobs and shutdown is false.
- A worker exits only when the queue is empty and shutdown is true, allowing queued work to drain after destruction starts.
- Jobs are popped FIFO from `head`, `tail` is cleared when the queue becomes empty, and `cond_full` is broadcast when the queue drops from full to not-full.
- `erofs_queue_work()` blocks while `job_count == max_jobs`, appends to the tail, increments count, signals `cond_empty`, and returns.
- `erofs_destroy_workqueue()` marks shutdown, wakes empty-waiting workers, joins all created workers in reverse order, frees the worker array, and destroys synchronization primitives.

## State And Data Structures

- `struct erofs_workqueue` owns head/tail pointers, worker array/count, max job count, current job count, shutdown flag, mutex, two condition variables, and optional hooks.
- `struct erofs_work` must provide a `next` pointer and callback.

## Dependencies

- POSIX pthreads and standard allocation.

## Risks And Invariants

- `erofs_queue_work()` does not reject enqueue after shutdown, so callers must not race queueing with destruction.
- If thread creation fails, `erofs_alloc_workqueue()` sets `nworker` to the number actually started and calls destroy to join them.
- `erofs_destroy_workqueue()` may return early on `pthread_join()` failure, leaving some cleanup incomplete.
