# File Research: sources/virtualization/qemu/block/aio_task.c

This file provides a small coroutine task-pool helper for running bounded numbers of asynchronous block-related tasks.

Key structures and functions:
- `AioTaskPool` tracks the main coroutine, first negative status, maximum concurrent tasks, current busy count, and whether the main coroutine is waiting.
- `aio_task_pool_new()` creates a pool bound to the current coroutine and asserts `max_busy_tasks > 0`.
- `aio_task_pool_start_task()` waits for capacity, assigns the pool to the task, and enters a newly created coroutine running `aio_task_co()`.
- `aio_task_co()` increments `busy_tasks`, runs `task->func(task)`, records the first negative return as pool status, frees the task, and wakes the main coroutine if needed.
- `aio_task_pool_wait_one()`, `aio_task_pool_wait_slot()`, and `aio_task_pool_wait_all()` implement capacity and completion waiting.
- `aio_task_pool_status()` returns zero for a null pool, allowing lazy pool allocation.

Concurrency model:
- This is coroutine-local coordination, not thread-level locking.
- The main coroutine is expected to be the only waiter and is asserted in `aio_task_pool_wait_one()`.
- Tasks are heap-owned by the pool once started; `aio_task_co()` frees them after completion.

Filesystem/block relevance:
- Used by block-copy style code to bound parallel copy workers while preserving coroutine scheduling semantics.
- Provides a simple failure propagation model: first failing task sets pool status, and later submitters can observe that failure.

Potential pitfalls:
- Only one waiter is modeled via `pool->waiting`.
- The pool must not be freed before all tasks finish; callers should use `aio_task_pool_wait_all()` before `aio_task_pool_free()`.
