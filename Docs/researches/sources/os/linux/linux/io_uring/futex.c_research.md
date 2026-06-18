# File Research: sources/os/linux/linux/io_uring/futex.c

## Purpose
Implements io_uring futex wait, futex waitv, futex wake, cancellation, and futex wait allocation caching.

## Main Structures
- `struct io_futex`: per-request parsed futex parameters.
- `struct io_futex_data`: single futex wait queue plus request pointer.
- `struct io_futexv_data`: ownership bit and flexible array of futex vectors.

## Main Functions
- Cache:
  - `io_futex_cache_init()`
  - `io_futex_cache_free()`
- Cancellation:
  - `io_futex_cancel()`
  - `io_futex_remove_all()`
  - `__io_futex_cancel()`
- Prep:
  - `io_futex_prep()`
  - `io_futexv_prep()`
- Wait/wake:
  - `io_futex_wait()`
  - `io_futexv_wait()`
  - `io_futex_wake()`
- Completion/wake callbacks:
  - `io_futex_complete()`
  - `io_futexv_complete()`
  - `io_futex_wake_fn()`
  - `io_futex_wakev_fn()`

## Important Design Points
- Wait requests are tracked inflight so file-exit cancellation can find them.
- Single futex waits allocate `io_futex_data` from `ctx->futex_cache`.
- Waitv requests allocate flexible vector storage and use an ownership bit to arbitrate wake-vs-cancel completion.
- Pending futex waits are linked on `ctx->futex_list` through `req->hash_node`.
- Completion is delivered via io_uring task_work.
- `io_futex_wake()` uses `FLAGS_STRICT` so waking zero futexes yields zero.

## Cross-File Relationships
- Declarations and config stubs are in `futex.h`.
- Uses generic cancel helpers from `cancel.c`.
- Uses allocation cache helpers from `alloc_cache`.
- Depends on kernel futex internals from `../kernel/futex/futex.h`.

## Risks / Review Notes
- Wake/cancel races are delicate, especially for waitv ownership.
- `io_futex_wait()` rejects a zero mask.
- `io_futexv_wait()` must restore task state to `TASK_RUNNING` after setup because async io_uring must not leave the task blocked like the synchronous futex syscall.
