# File Research: sources/os/linux/linux/fs/fuse/dev_uring.c

## Purpose
This file implements an optional io_uring command transport for FUSE requests. Instead of daemon `read(/dev/fuse)` and `write(/dev/fuse)`, userspace registers per-CPU ring entries with header and payload buffers, receives requests through io_uring command completions, and commits replies with `FUSE_IO_URING_CMD_COMMIT_AND_FETCH`.

## Main Definitions
- Module parameter `enable_uring` gates initial use of the transport.
- `struct fuse_uring_pdu` stores the active `fuse_ring_ent` pointer inside an io_uring command PDU.
- `fuse_io_uring_ops` replaces the FUSE input queue `send_req` operation once the ring is ready.
- Ring setup functions: `fuse_uring_create()`, `fuse_uring_create_queue()`, `fuse_uring_register()`, and `fuse_uring_create_ring_ent()`.
- Request/entry state functions: `fuse_uring_ent_avail()`, `fuse_uring_add_req_to_ring_ent()`, `fuse_uring_send_next_to_ring()`, `fuse_uring_commit()`, and `fuse_uring_next_fuse_req()`.
- Teardown functions: `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, `fuse_uring_entry_teardown()`, and async teardown work.
- Public entry point: `fuse_uring_cmd()`.

## Control Flow And Behavior
Userspace submits `FUSE_IO_URING_CMD_REGISTER` with a 128-byte SQE command containing a queue id and an iovec pair. The kernel creates the global ring and the target per-CPU queue if needed, validates the header/payload buffers, creates a `fuse_ring_ent`, marks the command cancelable, and places the entry on the available queue. When all queues have at least one available entry, the connection’s input queue ops switch to `fuse_io_uring_ops`, `ring->ready` becomes true, and blocked FUSE request allocators wake.

When a kernel request is queued over io_uring, it is assigned to the current task CPU’s queue. If an available entry exists, the request is bound to it and dispatched by completing task work in the ring task context so userspace buffer access permissions are correct. Otherwise the request waits on the queue’s request list. Background requests use a per-queue background list and `fuse_uring_flush_bg()` so each queue can make progress even under global background limits.

For replies, userspace submits `FUSE_IO_URING_CMD_COMMIT_AND_FETCH` with the committed request id. The kernel finds the request in the queue’s processing table, transitions the entry to commit state, copies the output header and payload from userspace buffers, completes the request, then immediately attempts to fetch and dispatch the next request on the same entry.

## Dependencies And Interfaces
The file depends on io_uring command APIs, FUSE request copy helpers from `dev.c`, FUSE processing queues, and the state structures declared in `dev_uring_i.h`. It is built under `CONFIG_FUSE_IO_URING`.

## Concurrency And Safety
Each `fuse_ring_queue` has a spinlock covering entry state transitions and queue lists. The connection lock protects ring creation and queue publication. `ring->queue_refs` tracks live entries through teardown; stopped queues prevent new assignments. Cancellation and teardown avoid immediate freeing of entries because io_uring cancellation can hold direct pointers into entries.

## Research Notes
Notifications and interrupt replies are not fully supported over the io_uring transport in this file; notifications are explicitly rejected in `fuse_uring_out_header_has_err()`, and the ops table keeps forget/interrupt on classic FUSE queue functions. The implementation emphasizes per-core affinity and commit-and-fetch batching to keep requests flowing.
