# File Research: sources/os/linux/linux-stable/fs/fuse/dev_uring_i.h

## Purpose
Defines private structures, states, declarations, and no-op fallbacks for the FUSE io_uring transport.

## Key Definitions
- `FUSE_URING_TEARDOWN_TIMEOUT` and `FUSE_URING_TEARDOWN_INTERVAL` control async teardown polling.
- `enum fuse_ring_req_state` defines entry lifecycle states: invalid, commit, available, assigned request, userspace, teardown, and released.
- `struct fuse_ring_ent` stores userspace header/payload pointers, owning queue, io_uring command, list node, state, and assigned FUSE request.
- `struct fuse_ring_queue` stores queue ID, lock, entry lists, request queues, embedded processing queue, active background count, and stopped flag.
- `struct fuse_ring` stores connection backpointer, queue count, max payload size, queue array, teardown/debug state, stop waitqueue, queue refcount, and readiness flag.

## Exported Internal API
When `CONFIG_FUSE_IO_URING` is enabled, it declares enablement, destruction, queue stop, abort completion, command handling, foreground/background queueing, pending removal, and timeout helpers. Inline helpers integrate abort and stopped-queue waiting with core `dev.c`.

## Fallback Behavior
When io_uring support is disabled, all helpers become no-ops or return false, preserving build-time compatibility for the core FUSE device code.

## Dependencies
Includes `fuse_i.h` and relies on structures defined by FUSE core plus io_uring command types when enabled.

## Research Notes
This header makes `dev.c` mostly feature-agnostic: core request allocation, timeout, abort, and wait paths can call io_uring hooks unconditionally while compilation removes them when disabled.
