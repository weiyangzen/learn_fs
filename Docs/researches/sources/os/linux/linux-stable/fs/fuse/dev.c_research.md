# File Research: sources/os/linux/linux-stable/fs/fuse/dev.c

## Purpose
Implements `/dev/fuse`, the core kernel/userspace transport for FUSE requests, replies, notifications, abort handling, request lifetime, splice support, background throttling, and miscdevice registration.

## Key Areas
- Request lifecycle: allocation, initialization, unique ID assignment, refcounting, waiting, interruption, completion, and freeing.
- Queues: input queue `fuse_iqueue`, per-device processing queue `fuse_pqueue`, background queue, forget queue, interrupt queue, and io_uring integration hooks.
- Userspace read path: `fuse_dev_do_read()` dequeues interrupts, forgets, or normal requests and copies request headers/args to userspace.
- Userspace write path: `fuse_dev_do_write()` parses reply headers, routes notifications, finds processing requests, copies output args, and completes requests.
- Copy engine: `fuse_copy_state`, page/folio copying, pipe splice support, optional folio stealing for page replacement.
- Notifications: poll wakeup, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Teardown: `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_release()`, request draining, poll wakeups, io_uring abort coordination.
- Ioctls: clone, passthrough backing open/close, and sync init.

## Design Notes
Foreground requests wait on per-request waitqueues; background requests are throttled by `max_background` and `active_background`. Interrupts are sent as special synthetic requests. Forget messages can be batched for protocol minor >= 16. Request timeout scanning checks pending, background, processing, and io_uring queues and aborts on expiry.

## Dependencies
Uses miscdevice, VFS file operations, pipes/splice, page cache/folios, FUSE protocol definitions, tracepoints, io_uring hooks, passthrough backing support, and proc fdinfo.

## Research Notes
This is the central synchronization point for FUSE. Lock ordering is carefully managed between connection locks, queue locks, request waitqueue locks, and copy operations that can fault. `FR_LOCKED`, `FR_ABORTED`, `FR_SENT`, `FR_PENDING`, and related flags are the primary request-state contract.
