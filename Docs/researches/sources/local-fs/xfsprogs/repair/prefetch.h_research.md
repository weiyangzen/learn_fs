# File Research: sources/local-fs/xfsprogs/repair/prefetch.h

## Role

`prefetch.h` declares the repair prefetch subsystem and its per-AG state structure.

## Interface

- `do_prefetch` enables or disables read-ahead globally.
- `PF_THREAD_COUNT` fixes four I/O workers per prefetch context.
- `prefetch_args_t` contains locks, condition variables, worker thread IDs, the I/O queue, AG number, state flags, throttling semaphore, and AG chaining pointer.
- `init_prefetch()`, `start_inode_prefetch()`, `do_inode_prefetch()`, `wait_for_inode_prefetch()`, and `cleanup_inode_prefetch()` form the public lifecycle.
- Optional `XR_PF_TRACE` hooks emit prefetch traces.

## Dependencies

It depends on pthreads, semaphores, repair `incore.h`, and the repair workqueue type.

## Risk Areas

Callers must pass `prefetch_args_t` through the intended wait/process/cleanup sequence; skipping cleanup would leak threads, conditions, semaphores, and queued buffers.
