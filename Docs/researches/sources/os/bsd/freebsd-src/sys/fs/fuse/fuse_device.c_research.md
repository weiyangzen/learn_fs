# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_device.c

## Purpose
Implements the `/dev/fuse` character device used by a userspace FUSE daemon to receive kernel requests and return replies/notifications.

## Main Elements
- Defines the character device switch with open, read, write, poll, and kqueue filter operations.
- `fuse_device_open()` allocates per-open `fuse_data` and attaches it as cdev private data.
- `fdata_dtor()` marks the session dead, wakes pollers, answers all awaiting tickets with `ENOTCONN`, drops unsent messages, optionally force-unmounts auto-unmount sessions, and tries to destroy session state.
- kqueue filters report read readiness when queued messages exist or the session is dead; write is always ready.
- `fuse_device_poll()` reports readable state for queued messages/dead sessions and always reports writable state.
- `fuse_device_read()` blocks or returns `EAGAIN` until a kernel-to-daemon message is queued, copies the full message to userspace, and kills the session on partial-read attempts.
- `fuse_ohead_audit()` validates reply body length and rejects replies with both error and body.
- `fuse_device_write()` reads a daemon reply header, optionally translates Linux errno values, validates format, finds the matching awaiting ticket, dispatches answer handlers, cleans related interrupt tickets, handles async notifications, and rejects missing tickets except likely stale interrupt `EAGAIN` replies.
- Notification handling supports invalidate-entry and invalidate-inode; retrieve/store/poll notifications are intentionally unimplemented.
- `fuse_device_init()` creates `/dev/fuse`; `fuse_device_destroy()` removes it.

## Dependencies And Integration
Connects `fuse_ipc` tickets/queues, FUSE mount/session state, VFS invalidation helpers, devfs cdev private storage, kqueue/poll, Linux errno compatibility, and forced unmount.

## Risk Notes
The daemon protocol boundary is defensive: malformed headers, unknown errno values, partial reads, and missing tickets can terminate or error the session. Correct ticket locking/refcounting is critical because reply handlers run without holding the awaiting-ticket mutex.
