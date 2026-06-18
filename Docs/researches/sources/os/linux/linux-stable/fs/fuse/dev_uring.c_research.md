# File Research: sources/os/linux/linux-stable/fs/fuse/dev_uring.c

## Purpose
Implements optional FUSE communication over io_uring, replacing the traditional split read/write `/dev/fuse` exchange with registered ring entries and `COMMIT_AND_FETCH` commands.

## Key Interfaces
- `fuse_uring_enabled()` reports the module parameter `enable_uring`.
- `fuse_uring_cmd()` handles io_uring passthrough commands: register and commit/fetch.
- `fuse_uring_register()` creates or finds the ring and queue, validates userspace iovecs, and registers a ring entry.
- `fuse_uring_commit_fetch()` commits the previous reply for a request and immediately fetches the next request into the same entry.
- `fuse_uring_queue_fuse_req()` queues foreground requests to a CPU-local ring queue.
- `fuse_uring_queue_bq_req()` queues background requests with per-queue dispatch.
- `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, and async teardown handle abort/shutdown.
- `fuse_uring_request_expired()` extends timeout detection to io_uring queues.

## Design Notes
The ring has one queue per possible CPU. Each queue owns available entries, entries with assigned requests, commit entries, userspace entries, released entries, foreground request queue, background request queue, and a FUSE processing queue for commit lookup.

Ring entries move through explicit states: commit, available, assigned FUSE request, userspace, teardown, and released. Registration only marks the ring ready after all queues have at least one available entry, then switches `fiq->ops` to io_uring operations and wakes blocked request allocation.

## Dependencies
Uses `io_uring_cmd`, FUSE copy helpers from `dev.c`, FUSE request/queue primitives, per-CPU task CPU selection, user iovec import, and connection abort logic.

## Research Notes
Notifications and interrupt replies are not fully transported through io_uring yet; forget and interrupt ops still use legacy queue helpers. Teardown intentionally delays freeing entries because io_uring cancellation may still hold direct entry pointers.
