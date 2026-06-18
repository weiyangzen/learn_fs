# File Research: sources/os/linux/linux/fs/fuse/dev.c

## Purpose
This file implements the main `/dev/fuse` kernel/userspace transport. It allocates and queues FUSE requests, copies request/reply payloads between kernel structures and userspace buffers or pipes, handles interrupts, background throttling, notifications, aborts, device cloning, passthrough backing ioctls, and miscdevice registration.

## Main Definitions
- `fuse_req_cachep` caches `struct fuse_req`.
- `fuse_timeout_timer_freq` and `fuse_check_timeout()` implement request timeout detection across pending, background, processing, and io_uring queues.
- Request lifecycle helpers include `fuse_request_init()`, `fuse_request_alloc()`, `fuse_get_req()`, `fuse_put_request()`, `fuse_request_end()`, and `request_wait_answer()`.
- Queue helpers include `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_dev_queue_req()`, `flush_bg_queue()`, `fuse_request_queue_background()`, and `fuse_simple_background()`.
- Copy helpers include `fuse_copy_init()`, `fuse_copy_finish()`, `fuse_copy_fill()`, `fuse_copy_do()`, `fuse_copy_folio()`, `fuse_copy_folios()`, `fuse_copy_args()`, and folio splice/move helpers.
- `/dev/fuse` data paths are `fuse_dev_do_read()` and `fuse_dev_do_write()`, wrapped by read/write/splice file ops.
- Notification handlers cover poll wakeups, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Abort/release/ioctl paths include `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_release()`, `FUSE_DEV_IOC_CLONE`, `FUSE_DEV_IOC_BACKING_OPEN`, `FUSE_DEV_IOC_BACKING_CLOSE`, and `FUSE_DEV_IOC_SYNC_INIT`.

## Control Flow And Behavior
Kernel-side filesystem operations allocate `fuse_req` objects through `fuse_get_req()`, which waits for connection initialization, background availability, and io_uring readiness as needed. It assigns pid/uid/gid in the FUSE header, respecting idmapped mount support. Synchronous requests are queued, then wait for a reply; background requests go through a throttled background queue.

`fuse_dev_do_read()` is the daemon’s request-fetch path. It waits for pending work, prioritizes interrupts, interleaves forget requests with normal requests, rejects too-small daemon buffers, moves reply-expected requests to the processing hash table, sets `FR_SENT`, and copies headers/arguments to userspace.

`fuse_dev_do_write()` is the daemon’s reply/notification path. It reads a `fuse_out_header`, dispatches unsolicited notifications when `unique == 0`, validates reply errors, finds the matching request in the processing hash, copies output arguments into the waiting request, and completes it. Interrupt replies have special handling for `ENOSYS` and `EAGAIN`.

The notification subsystem lets daemons invalidate cached inode/entry state, push data into the page cache, retrieve cached data by sending a `FUSE_NOTIFY_REPLY`, request resending of processing requests, increment an epoch to invalidate dentries, and prune specific inode nodeids.

Abort disconnects the connection, stops timeout work, marks processing queues disconnected, completes all pending/processing requests with `-ECONNABORTED`, frees forgets, wakes all waiters/pollers, and then invokes io_uring abort handling outside `fc->lock` to avoid lock-order conflicts.

## Dependencies And Interfaces
This is the central FUSE core file. It depends on FUSE internal headers, tracepoints, miscdevice APIs, poll/fasync, splice and pipe APIs, folio/page-cache APIs, user iov iterators, idmapped mount helpers, passthrough backing support, and optional `CONFIG_FUSE_IO_URING`.

## Concurrency And Safety
Important locks include `fiq->lock` for input pending/interrupt/forget queues, `fpq->lock` for per-device processing queues, `fc->bg_lock` for background throttling, `fc->lock` for connection/device lists, request waitqueue locks for `FR_LOCKED`/`FR_ABORTED`, and `fc->killsb` for reverse notifications that touch inode/dentry state. Memory barriers pair interrupt delivery, initialization visibility, and abort wakeups.

## Research Notes
This file defines the classic FUSE protocol transport semantics. io_uring is integrated by replacing `fiq->ops->send_req` when a ring becomes ready, but forget and interrupt paths still use the classic device queue operations in this implementation.
