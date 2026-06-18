# File Research: sources/os/linux/linux/fs/xfs/xfs_healthmon.c

Implements the XFS live health monitoring anonymous file descriptor used by privileged userspace, primarily a healer daemon, to receive filesystem health, shutdown, media, and file I/O error events.

Key elements:
- Defines a mount-attached `xfs_healthmon` lifetime model with RCU lookup, refcounting, weak mount cookies, a global attach/detach spinlock, and cleanup after all fd/mount/event-handler references drain.
- `xfs_ioc_health_monitor` validates privilege and ioctl format, creates a monitor, queues an initial RUNNING event, preallocates an UNMOUNT event, attaches to the mount, and returns an anonymous read-only fd.
- Event producers report filesystem, AG/rtgroup, inode, shutdown, media, and file-range I/O errors through `xfs_healthmon_report_*` helpers.
- Metadata health reporting filters old/new sick masks unless verbose mode is requested, and removes secondary health bits before emitting events.
- Queue handling merges compatible events: lost counters, health masks, shutdown flags, adjacent media ranges, and adjacent file ranges for the same inode generation.
- Queue pressure is bounded by `XFS_HEALTHMON_MAX_EVENTS`; allocation failure or full queue increments lost-event accounting, and the next successful push emits a LOST event.
- Read path uses a lazily allocated bounded output buffer, formats events into `struct xfs_health_monitor_event` v0 records, copies to userspace via `copy_to_iter`, and supports blocking/nonblocking reads.
- Poll exposes `EPOLLIN` when queued events, unread formatted bytes, or detach/EOF state is visible.
- File ioctls support monitor reconfiguration and checking whether an arbitrary fd belongs to the monitored filesystem.
- `/proc` fdinfo reports alive/dead state, dev_t, format, total events, and lost count.

Dependencies:
- Uses anonymous inode fd APIs, VFS read/poll/ioctl plumbing, wait queues, RCU, refcounting, mutexes, spinlocks, and user-copy helpers.
- Integrates with XFS mount state, health masks, tracing, shutdown flags, fserror events, realtime group/allocation group metadata, and ioctl ABI definitions.

Research notes:
- The monitor deliberately uses a weak mount reference so queued events and readers do not pin or slow unmount.
- Unmount queues a preallocated event before detaching so userspace can observe filesystem teardown even under memory pressure.
- Reads return EOF-like behavior after detachment when no data remains, allowing monitor daemons to exit cleanly.
- Only `CAP_SYS_ADMIN`, the root inode, and the initial user namespace can create the monitor fd.
