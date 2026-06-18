# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.c

## Purpose

Implements the live XFS health-monitor anonymous file descriptor used by privileged userspace, primarily the healer daemon, to receive structured filesystem health, shutdown, media-error, and file I/O error events.

## Main Responsibilities

- Manages the lifetime of `struct xfs_healthmon` objects with RCU-safe mount attachment, weak mount cookies, refcounts, and fd release handling.
- Queues health events from filesystem code, coalescing compatible adjacent or duplicate events to reduce userspace traffic.
- Tracks queue overflow through synthetic lost-event notifications and cumulative fdinfo counters.
- Formats internal health events into `struct xfs_health_monitor_event` v0 records for `read_iter`.
- Implements fd operations for `read_iter`, `poll`, `release`, `show_fdinfo`, and health-monitor ioctls.
- Creates the health monitor fd from `XFS_IOC_HEALTH_MONITOR` with capability, root-inode, and initial user-namespace checks.

## Key Data Flow

Events enter through report helpers:

- `xfs_healthmon_report_fs`
- `xfs_healthmon_report_group`
- `xfs_healthmon_report_inode`
- `xfs_healthmon_report_shutdown`
- `xfs_healthmon_report_media`
- `xfs_healthmon_report_file_ioerror`
- `xfs_healthmon_unmount`

Each helper obtains the active monitor through `xfs_healthmon_get`, builds an `xfs_healthmon_event`, and calls `xfs_healthmon_push`. The queue is protected by `hm->lock`; mount-to-monitor pointer updates are protected by `xfs_healthmon_lock` and RCU.

Userspace reads from the anonymous fd. `xfs_healthmon_read_iter` waits for queued events or buffered bytes, formats events into `hm->buffer` with `xfs_healthmon_format_v0`, and copies bytes to the supplied iterator.

## Event Semantics

- `RUNNING` is queued first when the fd is created.
- `UNMOUNT` is preallocated at fd creation time and inserted at the head of the event list during unmount so userspace sees teardown promptly.
- Metadata events are filtered by `metadata_event_mask`; verbose mode reports all changed bits, non-verbose mode reports runtime sickness, newly found fsck corruption, or repaired health transitions.
- Secondary health flags are filtered before reporting filesystem, AG, rtgroup, and inode metadata events.
- Media errors map XFS data/log/realtime devices to health-monitor domains.
- File I/O errors map `fserror_type` actions to buffered, direct I/O, or data-loss event types and return positive errno values to userspace.

## Important Invariants

- Only one health monitor may be attached to an `xfs_mount` at a time.
- `mount_cookie` is a weak superblock pointer value and must not be dereferenced except under the attach/detach protocol used here.
- `DETACHED_MOUNT_COOKIE` makes future event pushes return shutdown and causes reads/poll to observe EOF-ready state.
- The event queue is capped by `XFS_HEALTHMON_MAX_EVENTS`; allocation failure or queue saturation increments lost-event counters.
- Output buffer size is bounded by `XFS_HEALTHMON_MAX_OUTBUF` and at least one page.
- Anonymous fd creation happens last because installed fds cannot be safely undone.

## Dependencies

- Uses `anon_inode_getfd`, poll, wait queues, and iterator copying for the fd interface.
- Uses health conversion helpers from `xfs_health.h`.
- Receives I/O error reports through Linux `fserror` plumbing.
- Integrates with mount state via `mp->m_healthmon`.
- Emits tracepoints for creation, insert, push, merge, drop, read, and release paths.

## Risk Notes

The code is concurrency-sensitive. The most important correctness points are the RCU/refcount handoff in `xfs_healthmon_get`, detaching before final fd release, preallocating the unmount event, and preserving queue accounting when events merge or are lost.
