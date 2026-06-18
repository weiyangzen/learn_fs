# File Research: sources/os/linux/linux/fs/xfs/xfs_healthmon.h

Declares the internal XFS health monitor state, event representation, event type/domain enums, and reporting entry points.

Key elements:
- `struct xfs_healthmon` stores a weak mount cookie, device number, refcount, event queue, preallocated unmount event, verbose flag, wait queue, read formatting buffer, and event/lost counters.
- `enum xfs_healthmon_type` covers monitor lifecycle, metadata health, shutdown, media error, buffered/direct I/O, and data loss events.
- `enum xfs_healthmon_domain` distinguishes mount, filesystem, AG, inode, realtime group, devices, and file ranges.
- `struct xfs_healthmon_event` is an internal tagged event object with union payloads for lost counts, health masks, group ids, inode identity, shutdown flags, media ranges, and file ranges.
- Declares reporting hooks for fs/group/inode health, shutdown, media errors, file I/O errors, unmount, and monitor ioctl creation.

Dependencies:
- Depends on XFS mount, group, inode, device, daddr, ino, and ioctl ABI types.
- Mirrors but does not expose directly the userspace `struct xfs_health_monitor_event` format used in `xfs_healthmon.c`.

Research notes:
- `mount_cookie` is explicitly documented as non-dereferenceable by users of the monitor object except guarded internal attach/detach logic.
- The event object stores inode generation numbers and file positions so userspace can correlate file-range errors without retaining kernel inode pointers.
