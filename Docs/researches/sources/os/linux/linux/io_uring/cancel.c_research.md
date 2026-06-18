# File Research: sources/os/linux/linux/io_uring/cancel.c

## Purpose
Implements io_uring async and sync cancellation across io-wq work, poll, waitid, futex, timeout, uring command, deferred, iopoll, and task-exit paths.

## Main Functions
- Matching and basic cancellation:
  - `io_cancel_req_match()`: matches requests by context, fd, opcode, user data, any/all flags, and cancel sequence.
  - `io_async_cancel_prep()`: validates cancel SQE and imports match criteria.
  - `io_try_cancel()`: tries io-wq, poll, waitid, futex, and timeout cancellation.
  - `io_async_cancel()`: executes an async cancel request and completes it.
- Sync cancellation:
  - `io_sync_cancel()`: handles registered sync cancel with optional timeout, fd lookup, wait/retry loop, and task work execution.
- Shared list helpers:
  - `io_cancel_remove_all()`
  - `io_cancel_remove()`
  - `io_match_task_safe()`
- Task/ring teardown:
  - `io_uring_try_cancel_requests()`: cancels outstanding requests for a context/task.
  - `io_uring_cancel_generic()`: exit/exec cancellation loop for a task’s io_uring contexts.
  - `__io_uring_cancel()`: unregisters ring fd and invokes generic cancel.
- Specialized helpers:
  - `io_cancel_defer_files()`
  - `io_uring_try_cancel_iowq()`
  - `io_cancel_ctx_cb()`

## Important Design Points
- `CANCEL_FLAGS` whitelists supported userspace cancel flags.
- Cancel matching defaults to user data when neither fd nor opcode matching is requested.
- `cancel_seq` prevents an `ASYNC_CANCEL_ALL` style operation from matching the same request repeatedly.
- `io_try_cancel()` continues past `-EALREADY` from io-wq to unarm poll/timeouts where possible.
- Sync cancel with `-EALREADY` waits on `ctx->cq_wait`, runs task work, and retries until completion, timeout, signal, or no matching request.
- Exit cancellation drains multiple sources: io-wq, iopoll, local task work, deferred files, poll, waitid, futex, uring_cmd, and timeouts.

## Cross-File Relationships
- Declared in `cancel.h`.
- Calls into `io-wq`, `poll`, `timeout`, `waitid`, `futex`, `uring_cmd`, `sqpoll`, `tw`, and resource/file helpers.
- Used by fdinfo to display poll/cancel table state.

## Risks / Review Notes
- Cancellation correctness depends on each subsystem exposing pending and running requests consistently.
- `io_match_task_safe()` must take `timeout_lock` for linked timeout races.
- Sync cancel temporarily drops `uring_lock` while waiting and must reacquire it before returning.
- Fixed-file cancellation must repeatedly look up fixed slots because `uring_lock` can be dropped.
