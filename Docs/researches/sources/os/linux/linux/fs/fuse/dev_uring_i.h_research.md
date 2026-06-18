# File Research: sources/os/linux/linux/fs/fuse/dev_uring_i.h

## Purpose
This internal header declares the FUSE io_uring transport data structures, state enum, public functions, and no-op stubs used when `CONFIG_FUSE_IO_URING` is disabled.

## Main Definitions
- `FUSE_URING_TEARDOWN_TIMEOUT` and `FUSE_URING_TEARDOWN_INTERVAL` control async teardown logging/retry timing.
- `enum fuse_ring_req_state` defines entry states:
  - `FRRS_INVALID`
  - `FRRS_COMMIT`
  - `FRRS_AVAILABLE`
  - `FRRS_FUSE_REQ`
  - `FRRS_USERSPACE`
  - `FRRS_TEARDOWN`
  - `FRRS_RELEASED`
- `struct fuse_ring_ent` stores userspace header/payload pointers, owning queue, io_uring command pointer, list node, state, and bound `fuse_req`.
- `struct fuse_ring_queue` stores queue id, lock, entry lists, pending/background request lists, a processing queue, active background count, and stopped flag.
- `struct fuse_ring` stores the parent `fuse_conn`, queue count, maximum payload size, queue array, stop diagnostics, waitqueue, async teardown work, queue refcount, and readiness flag.

## Interfaces
When enabled, the header declares:
- `fuse_uring_enabled()`
- `fuse_uring_destruct()`
- `fuse_uring_stop_queues()`
- `fuse_uring_abort_end_requests()`
- `fuse_uring_cmd()`
- `fuse_uring_queue_fuse_req()`
- `fuse_uring_queue_bq_req()`
- `fuse_uring_remove_pending_req()`
- `fuse_uring_request_expired()`

It also defines inline helpers:
- `fuse_uring_abort()` aborts requests and stops queues when live queue refs exist.
- `fuse_uring_wait_stopped_queues()` waits for queue refs to reach zero.
- `fuse_uring_ready()` tests connection ring readiness.

When disabled, the same helpers compile to no-ops or `false`, and pending request removal/request expiry return `false`.

## Research Notes
The header makes the rest of FUSE mostly compile-time agnostic to io_uring support. The state enum is the key to understanding `dev_uring.c`: entries transition from available, to assigned request, to userspace, to commit, and eventually back to available or into teardown/released states.
