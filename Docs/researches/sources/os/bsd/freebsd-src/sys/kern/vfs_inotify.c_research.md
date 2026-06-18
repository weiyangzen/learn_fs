# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_inotify.c

## Role

Implements FreeBSD's inotify-compatible descriptor, watch, event queue, and vnode notification integration. It exposes inotify file operations and kernel helpers used by VFS/vnode code to create, remove, and log watches.

## Main Entry Points

- `inotify_create_file()` initializes an inotify descriptor and installs `inotifyfdops`.
- `kern_inotify_add_watch()` validates masks, resolves the watched path, enforces access and watch limits, and delegates to `VOP_INOTIFY_ADD_WATCH()`.
- `vn_inotify_add_watch()` creates or updates a watch on a vnode.
- `kern_inotify_rm_watch()` removes a watch by watch descriptor and queues `IN_IGNORED`.
- `vn_inotify()` converts vnode/directory events into inotify self and parent-directory notifications.
- `inotify_log()` and `inotify_log_one()` enqueue matching events for watchers.
- File operations include `inotify_read()`, `inotify_ioctl()`, `inotify_poll()`, `inotify_kqfilter()`, `inotify_stat()`, `inotify_close()`, and `inotify_fill_kinfo()`.

## Data Structures

`struct inotify_softc` represents one descriptor. It contains a mutex, pending event queue, preallocated overflow record, watch descriptor allocator, byte/event pending counts, RB tree of active watches, list of dead watches waiting for asynchronous `vrele()`, a taskqueue reap task, selinfo/knote state, and held credentials.

`struct inotify_watch` links a descriptor to a watched vnode, with RB-tree linkage by watch descriptor and TAILQ linkage from vnode pollinfo. `struct inotify_record` stores an `inotify_event` plus variable-sized name payload.

## Event Queue Behavior

Reads block unless nonblocking flags are set. They dequeue as many records as fit in the user buffer, requeue the first record and return `EINVAL` if the first event cannot fit, and reuse the per-descriptor overflow record after it is read.

`inotify_queue_record()` coalesces duplicate tail events when enabled, enforces `max_queued_events`, converts queue or allocation failures to `IN_Q_OVERFLOW`, updates drop counters, and wakes `select`, `poll`, `kqueue`, and blocking readers.

## Watch Behavior

Adding a directory watch first populates name-cache state for existing entries so later vnode-only events can be associated with names. Existing watches on the same descriptor/vnode are updated unless `IN_MASK_CREATE` forbids replacement. New watch descriptors avoid reuse as long as possible.

One-shot watches and self-delete/unmount events queue `IN_IGNORED` and remove the watch from the descriptor and vnode. Vnode reference release is deferred to a taskqueue when removal happens from notification context.

## Limits And Tuning

Sysctls control max queued events, max instances per user, max watches per user, max watches system-wide, current watches, event coalescing, and event drop count. Defaults for user and system watch limits are derived from `desiredvnodes`.

## Locking And Lifetime

Descriptor state is serialized by `sc->lock`. Vnode watch lists are protected by `vp->v_pollinfo->vpi_lock`. The code carefully orders these locks when adding, logging, removing, and closing watches. Watch counts are tracked both globally and per real UID.

## Dependencies

This file depends on vnode pollinfo, name cache support (`cache_vop_inotify()`), VOP hooks (`VOP_INOTIFY_ADD_WATCH`, `VOP_GETATTR`, `VOP_ACCESS`), Capsicum rights for inotify operations, taskqueue cleanup, kqueue/select/poll integration, and resource counters.

## Notes

The implementation is compatibility-oriented: removed-watch events do not purge already queued events, watch descriptors are not aggressively reused, and overflow handling uses Linux-style `IN_Q_OVERFLOW`.
