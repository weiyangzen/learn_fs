# File Research: sources/os/linux/linux/io_uring/io-wq.h

## Purpose
Declares the io_uring worker-queue API, work flags, cancellation results, and worker detection helpers.

## Main Contents
- Work flags:
  - `IO_WQ_WORK_CANCEL`
  - `IO_WQ_WORK_HASHED`
  - `IO_WQ_WORK_UNBOUND`
  - `IO_WQ_WORK_CONCURRENT`
  - `IO_WQ_HASH_SHIFT`
- `enum io_wq_cancel`: pending-canceled, running-cancel-attempted, or not-found.
- `struct io_wq_hash`: shared hash serialization map and waitqueue.
- `struct io_wq_data`: creation inputs containing hash and owner task.
- API declarations:
  - create/exit/put, exit-on-idle, enqueue, hash work, CPU affinity, max workers, worker stopped, cancel callback.
- Scheduler hook declarations under `CONFIG_IO_WQ`.
- `io_wq_current_is_worker()`: detects current io-wq worker tasks via `PF_IO_WORKER` and `worker_private`.

## Cross-File Relationships
- Implemented by `io-wq.c`.
- Used by core io_uring, cancellation, eventfd, and async submission paths.

## Risks / Review Notes
- Hash bits are stored in the upper bits of work flags; new flags must not collide with `IO_WQ_HASH_SHIFT` encoding.
- `io_wq_current_is_worker()` depends on scheduler task flags and `current->worker_private` being set by io-wq worker setup.
