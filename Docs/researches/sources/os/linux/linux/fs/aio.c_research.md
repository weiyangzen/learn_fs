# File Research: sources/os/linux/linux/fs/aio.c

## Summary
Implements Linux native asynchronous I/O syscalls and their completion ring infrastructure. It manages AIO contexts, ring mmap setup, request accounting, cancellation, completion delivery, polling, fsync work, compat syscalls, and teardown.

## Main Responsibilities
- Provide `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents`.
- Allocate `kioctx` contexts and map userspace-visible completion rings.
- Maintain per-mm RCU-protected AIO context tables.
- Track global and per-context request limits.
- Submit read/write, vectored read/write, fsync/fdsync, and poll requests.
- Deliver completions into shared rings and optionally signal eventfds.
- Cancel active requests and destroy contexts on `io_destroy()` or `exit_aio()`.

## Key APIs
- Syscalls: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, `io_pgetevents`, plus compat/time32 variants.
- Internal lifecycle: `ioctx_alloc()`, `kill_ioctx()`, `exit_aio()`, `lookup_ioctx()`.
- Request helpers: `aio_get_req()`, `iocb_put()`, `aio_complete()`, `aio_complete_rw()`.
- Operation handlers: `aio_read()`, `aio_write()`, `aio_fsync()`, `aio_poll()`.
- Exported helper: `kiocb_set_cancel_fn()`.

## Important Behavior
AIO rings are backed by an internal pseudo filesystem and an anonymous file mapped into the caller’s address space. The userspace handle is the mmap base address; lookup reads the ring id from userspace and verifies it against the current mm’s context table.

Ring slots are protected by a batched per-cpu `reqs_available` scheme. Completions update the kernel tail and userspace ring tail under `completion_lock`, then wake waiters whose `min_nr` is satisfied.

Request lifetime uses two references: one for the async completion path and one for synchronous submission cleanup. Context lifetime uses percpu refs for users and outstanding requests, with final freeing deferred through RCU work.

Poll AIO uses waitqueue entries, RCU protection for `wake_up_pollfree()`, cancellation callbacks, and optional workqueue completion when inline completion is unsafe.

## State and Synchronization
Uses `mm->ioctx_lock`, RCU, percpu refs, `ctx_lock`, `ring_lock`, `completion_lock`, waitqueues, hrtimers, workqueues, eventfd references, file references, and page migration hooks. Ring folio migration is serialized with `ring_lock`, `migrate_lock`, and `completion_lock`.

## Risks
This is concurrency-heavy legacy infrastructure. Correctness depends on precise ordering between userspace ring head/tail, completion writes, request-slot refill, context table removal, cancellation, poll waitqueue freeing, and RCU-delayed context free. The userspace ring head is intentionally trusted only after clamping.
