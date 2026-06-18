# File Research: sources/os/linux/linux-stable/fs/eventfd.c

This file implements Linux `eventfd`, a pollable anonymous-file counter used by userspace and kernel subsystems for event notification.

Major responsibilities:
- Defines `struct eventfd_ctx` with a kref, waitqueue, 64-bit counter, flags, and fdinfo id.
- Implements kernel signaling through `eventfd_signal_mask()`, exported for in-kernel users.
- Implements read/write/poll/release file operations for eventfd anonymous inodes.
- Provides fdinfo output under procfs when enabled.
- Provides kernel helpers:
  - `eventfd_fget()`
  - `eventfd_ctx_fdget()`
  - `eventfd_ctx_fileget()`
  - `eventfd_ctx_put()`
  - `eventfd_ctx_do_read()`
  - `eventfd_ctx_remove_wait_queue()`
- Implements `eventfd2` and legacy `eventfd` syscalls.

Counter semantics:
- Writes add a user-supplied `u64` value, except `ULLONG_MAX` is invalid.
- Reads return and clear the full count, or return/decrement by one in `EFD_SEMAPHORE` mode.
- Kernel `eventfd_signal_mask()` increments by one and may let the counter reach `ULLONG_MAX`, which poll reports as `EPOLLERR`.
- Poll reports readable when count is nonzero, writable when at least one less than `ULLONG_MAX`, and error on overflow.

Concurrency and wakeups:
- `ctx->wqh.lock` protects `count` and waitqueue operations.
- Poll relies on `poll_wait()` waitqueue locking as an ordering barrier, allowing a lockless `READ_ONCE(ctx->count)` after registration.
- Wakeups set `current->in_eventfd` to avoid recursive waitqueue wakeups causing deadlock or stack overflow.
- Release wakes waiters with `EPOLLHUP` and drops the context reference.
- `eventfd_ctx_remove_wait_queue()` atomically removes a waitqueue entry and reads/resets the counter under the same lock.

Resource lifetime:
- Contexts are reference-counted with `kref`.
- IDs are allocated with a global `IDA` for fdinfo and freed with the context.
- Anonymous file creation uses the eventfd fops and publishes the prepared fd only after setup succeeds.
